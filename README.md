# NeonAI API Proxy
Proxies API calls to consolidate usage to a single point and allow for caching of API data.

## Request Format
API requests should be in the form of a dictionary. The service requested should be specified as `service` and the 
remaining data will be passed to the `handle_query` method of the requested service as kwargs.

>Example Wolfram|Alpha Request:
>```json
>{
>  "service": "wolfram_alpha",
>  "query": "how far away is Rome?",
>  "api": "simple",
>  "units": "metric",
>  "ip": "64.34.186.120"
>}
>```

## Response Format
Responses will be returned as dictionaries. Responses should contain the following:
- `status_code` - Usually contains the HTTP status code from the requested API, `-1` should be used to specify any other errors
- `content` - Usually contains the HTTP content (bytes) from the requested API, but may include a string message for errors.
- `encoding` = Usually contains the HTTP content encoding if content is the byte representation of a string, may be `None`

## Docker Configuration
When running this as a docker container, the path to configuration files should be mounted to `/config`.

For example, if your configuration resides in `~/.config`:
```commandline
docker run -v /home/$USER/.config:/config neon_api_proxy
```
