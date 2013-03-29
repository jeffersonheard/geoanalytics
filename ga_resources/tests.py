from ga_resources import drivers

drivers.render(
    'png',
    512,512,
    (-180,-90,90,180),
    "+init=epsg:4326",
    ['world-borders/basic-style-for-world-borders'],
    ['world-borders/world-borders-wms']
)