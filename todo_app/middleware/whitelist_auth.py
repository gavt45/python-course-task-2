from typing import List
import logging

from fastapi.exceptions import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from fastapi import Request
from hashlib import sha256

from ipaddress import ip_address, ip_network

class IPWhitelistAuthScheme:
    def __init__(
        self,
        cidrs: List[str],
        trusted_proxy_nets: List[str] = [],
        trusted_proxy_headers: List[str] = ['x-forwarded-for'],
        auto_error: bool = True,
    ):
        """
        Parameters
        ----------
        cidrs : List[str]
            list of allowed client CIDRS
        trusted_proxy_nets : List[str]
            list of allowed proxy networks
        trusted_proxy_headers : List[str]
            list of proxy headers to check client address from if request is from trusted proxy net
        auto_error : bool
            if True raises HTTPException automatically
        """
        if not cidrs or len(cidrs) == 0:
            raise RuntimeError("IPWhitelistAuthScheme cidr list is empty!")
        
        self._cidrs = [ip_network(c) for c in cidrs]
        self._trusted_proxy_nets = [ip_network(c) for c in trusted_proxy_nets]
        self._trusted_proxy_headers = set(trusted_proxy_headers)
        self._auto_error = auto_error
        

    async def __call__(self, request: Request) -> bool:
        # logging.debug(f"Client IP: {request.client.host}")
        is_from_whitelisted = False

        cli_host = ip_address(request.client.host)

        for header_name in self._trusted_proxy_headers:
            # if has header 'x-forwarded-for' or so
            if header_name in request.headers:
                for trusted_proxy_net in self._trusted_proxy_nets:
                    # if request comes from trusted proxy net
                    if cli_host in trusted_proxy_net:
                        # set client host to header value
                        cli_host = ip_address(request.headers[header_name])
                        break
                else:
                    logging.warn(f"Request with {header_name} from non-trusted net!")


        for c in self._cidrs:
            if cli_host in c:
                is_from_whitelisted = True
                break

        
        if not is_from_whitelisted:
            if self._auto_error:
                logging.warn(f"Request from non whitelisted address: {request.client.host}")
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not whitelisted address",
                )
            else:
                return False
        
        return True