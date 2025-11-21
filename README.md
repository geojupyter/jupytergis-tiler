<p align="center" width="100%">
<video src="https://github.com/user-attachments/assets/5c2d669a-ff8c-4a66-97e3-1845220fb819" width="80%" controls></video>
</p>

# jupytergis-tiler

A JupyterGIS extension for creating and serving raster layers using your own data.

## Install from PyPI

Rasterio currently doesn't ship wheels for Python 3.14, so be sure to pin `python <3.14` for now.

Also, there is currently an incompatibility between JupyterLab 4.5 and jupyter-collaboration 3.
Until JupyterGIS supports jupyter-collaboration 4, you should pin `jupyterlab <4.5`.

```bash
pip install jupytergis-tiler
```

## Development install

Clone or fork this repository and:

```bash
pip install .
```

## Usage

First create a `GISDocument` in a cell and display it:

```py
doc = GISDocument("my_file.jGIS")
doc
```

Say you have a `xarray.DataArray` called `da` with geographical coordinates,
you can show it as a raster layer like so:

```py
await doc.add_tiler_layer(
    name="My layer",
    data_array=da,
)
```

Please look at the notebooks in the `examples` directory.
