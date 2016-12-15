Contains special nginx directives.

List all available server names in `http-server_name.conf`. The server name directive is included in each server directive.

For proxying applications which are not hosted on localhost, you can define upstreams in `http-upstreams.conf` and the locations based on that upstreams in `http-locations.conf`.

For proxying additional streams, use `stream.conf`.
