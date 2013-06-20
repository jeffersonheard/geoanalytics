Resources
=========

One of the principle components of Geoanalytics is its Geographic Content Managment System (CMS). The CMS uses standard
metaphors from content management systems like Wordpress (in this case, we use Mezzanine) and maps them to the kinds of
building blocks needed to build geospatial applications and perform analytics. This encourages publishers of data to
provide content in a discoverable, searchable way, and shortens the path to publishing metadata, textual descriptions,
and results. Using metaphors that are familiar such as pages, blog posts, and links, Geoanalytics provides a "friendly"
interface to data users.

A Data Resource is a special kind of page which contains geographic data or the configuration needed to reach remote
geographic data. Every dataset Geoanalytics has access to corresponds to a Data Resource.

Every resource is defined by:

    * Title
    * Content description, a rich text description of the dataset itself
    * Metadata keywords
    * A link to the content (A URL, either generated from an uploaded file or provided by the data publisher)
    * A driver capable of inspecting the content and providing basic metadata introspection and extensive data access
      services.

Defining a resource in Geoanalytics gives you:

    * A permanent link to the dataset
    * A "slug" or shortened, machine-readable name that can be used to refer to the dataset in analytics programs
    * An API into the dataset that can be accessed through analytics programs defined on the Geoanalytics server
    * A descriptive page that combines provided content with automatically inspected metadata
    * The ability to publish a number of other derived services as pages, such as WMS or (coming soon) WFS services that
      expose the data in a unique way

Currently supported data types
------------------------------

    * GDAL compatible datasets
    * Shapefile packages
    * OGR compatible datasets
    * PostGIS
    * Django models

Customizing the presentation of data
------------------------------------

Linking data to other services
------------------------------


