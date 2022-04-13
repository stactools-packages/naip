# stactools-naip

stactools-naip is a [stactools](https://github.com/stac-utils/stactools) package to generate STAC objects
for NAIP images.

## How to use

To install, run:

```shell
pip install stactools-naip
pip install stactools[s3]
```

To create a STAC Item:

```shell
aws s3 cp --request-payer requester s3://naip-analytic/va/2018/60cm/fgdc/37077/m_3707763_se_18_060_20180825.txt .
export AWS_REQUEST_PAYER='requester'
stac naip create-item --fgdc m_3707763_se_18_060_20180825.txt \
  VA 2018 s3://naip-analytic/va/2018/60cm/rgbir_cog/37077/m_3707763_se_18_060_20180825.tif \
  json-dest/
```

## Development

```shell
pip install -r requirements-dev.txt
```


Install pre-commit hooks with:

```shell
pre-commit install
```

Run these before commit with:

```shell
pre-commit run --all-files
```
