# korto-exporter

A custom [Prometheus exporter][] for exporting metrics from [korto.ee][] residence management system.

It allows an apartment resident to export their apartment utility meter readings and invoice data as Prometheus metrics.

## Usage

This is designed to be run in a Docker container. Deploy it to your Docker platform of choice.

```bash
$ docker run -p 8080:8080 -e KORTO_AUTH_TOKEN=xxxxx -e KORTO_APARTMENT_ID=xxxx anroots/korto-exporter
```

Configure a new Prometheus target to scrape the exposed endpoint. As (regardless of what one might expect) the Korto
system is not really real-time automagical, it doesn't make sense to configure scraping frequency of more than once
or twice a day.

```yaml

```

### Environment variables

| Variable name | Description | Default value | Required | 
| ------------- | ----------- | ------------- | -------- |
| KORTO_AUTH_TOKEN | JWT token to access the Korto API. Log in via the korto.ee web interface, open browser dev tools -> Application -> Cookies; value of `auth_token` cookie    | `None`     | Yes |
| KORTO_API_URL      | HTTPS URL to the korto.ee API endpoint | `https://pro.korto.ee/api/` | No |
| KORTO_APARTMENT_ID | Your apartment ID in the Korto system. You can only view apartments belonging to you; this exporter currently only supports a single apartment ID at a time. Get it from browser dev tools -> Application -> Local Storage -> `currentObjectId` value| | |
| LOG_LEVEL| Exporter log level (to stdout)| `INFO` | No |


## Development

Use the included `docker-compose.yml` file for development..

```bash
$ docker-compose up
```

...or install dependencies to Python venv, and debug locally:

```bash
$ pip install -r requirements.txt
$ python src/collector.py
```

## References

- https://korto.ee/abi/
- https://comserv.cs.ut.ee/home/files/Puusepp_Informaatika_2018.pdf?study=ATILoputoo&reference=EB5FBF165A77B801D3408E109F988398C3B3EC42
- https://digikogu.taltech.ee/et/Item/c6cd968c-67b6-41e8-826a-3918f7fee948


[Prometheus exporter]: https://prometheus.io/docs/instrumenting/writing_exporters/
[korto.ee]: https://korto.ee
