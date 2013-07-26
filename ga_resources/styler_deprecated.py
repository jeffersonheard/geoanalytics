class StylerView(TemplateView):
    template_name = 'ga_resources/styler.html'

    def get_context_data(self, **kwargs):
        ctx = super(StylerView, self).get_context_data(**kwargs)
        ctx['installed_fonts'] = ['DejaVu Sans Book']

        resource_slug = self.request.GET['resource']
        resource = models.DataResource.objects.get(slug=resource_slug)

        drv = resource.driver_instance
        df = drv.as_dataframe()
        keys = [k for k in df.keys() if k != 'geometry']
        type_table = {
            'float64': 'number',
            'int64': 'number',
            'object': 'text'
        }
        ctx['resource'] = resource
        ctx['new_service'] = 'new' in self.request.GET and self.request.GET['new']

        ctx['attrs'] = [{'name': k} for k in keys]
        for i, k in enumerate(keys):
            s = df[k]
            ctx['attrs'][i]['kind'] = type_table[s.dtype.name]
            ctx['attrs'][i]['tags'] = [tag for tag in [
                'unique' if predicates.unique(s) else None,
                'not null' if predicates.not_null(s) else None,
                'null' if predicates.some_null(s) else None,
                'empty' if predicates.all_null(s) else None,
                'categorical' if predicates.categorical(s) else None,
                'open ended' if predicates.continuous(s) else None,
                'mostly null' if predicates.mostly_null(s) else None,
                'uniform' if predicates.uniform(s) else None
            ] if tag]
            if 'categorical' in ctx['attrs'][i]['tags']:
                ctx['attrs'][i]['uniques'] = [x for x in s.unique()]
            for k, v in s.describe().to_dict().items():
                ctx['attrs'][i][k] = v
        ctx['attrs'] = json.dumps(ctx['attrs'], indent=2)

        return ctx


class SaveStyleView(View):
    #
    # this probably all moves to its own view module.  It creates stylesheet entries, or at least I hope it does.
    #
    def maybe_string(self, v):
        try:
            return float(v)
        except:
            return '"' + v + '"' # fixme properly escape quotes and stuff

    def maybe_equals(self, v):
        try:
            _ = float(v)
            return ">="
        except:
            return "="


    def css_values(self, selector, summary):
        if summary == 'default':
            return None, [""]
        elif summary['kind'] == 'uniform':
            return None, ["Layer {{ {selector} : {value} }}".format(
                selector=selector,
                value=summary['value']
            )]
        elif summary['kind'] == 'spread':
            segments = summary['segments']
            min_o = summary['min']
            max_o = summary['max']
            attribute = summary['attribute']
            opacity = np.linspace(min_o, max_o, len(segments))
            return None, ["Layer [{attr} {op} {value}] {{ {key}: {j}; }}".format(
                attr=attribute,
                value=self.maybe_string(v),
                op=self.maybe_equals(v),
                key=selector,
                j=opacity[i]
            )
                          for i, v in enumerate(segments)]
        elif summary['kind'] == 'palette':
            palette = summary['palette']
            n = summary['n']
            segments = summary['segments']
            return palette, ["""Layer [{attr} {op} {value}] {{ {key}: @{palette}_{n}_{i}; }}""".format(
                attr=summary['attribute'],
                value=self.maybe_string(v),
                op=self.maybe_equals(v),
                key=selector,
                palette=palette,
                n=n,
                i=i
            ) for i, v in enumerate(segments)]
        elif summary['kind'] == 'labels':
            text_face_name = summary['font']
            text_size = summary['textSize']
            text_color = summary['textColor']
            attribute = summary['attribute']
            return None, ["""
Layer {attribute} {{
    text-face-name: "{text_face_name}";
    text-size: {text_size};
    text-color: {text_color};
}}""".format(
                attribute=attribute,
                text_face_name=text_face_name,
                text_size=text_size,
                text_color=text_color
            )]

    def post(self, request, *args, **kwargs):
        summary = json.loads(request.POST['stylesheet'])
        existing_or_new = request.POST['existing_or_new']
        existing_layer_name = request.POST['existing_layer_name']
        new_layer_name = request.POST['new_layer_name']
        style_name = request.POST['style_name']
        resource = request.POST['resource']

        print request.POST['stylesheet']

        stylesheet = []
        palette1, polygon_fill = self.css_values('polygon-fill', summary['polygon-fill'])
        stylesheet.extend(polygon_fill)

        stylesheet.extend(self.css_values('polygon-opacity', summary['polygon-opacity'])[1])
        palette2, line_color = self.css_values('line-color', summary['line-color'])
        stylesheet.extend(line_color)
        stylesheet.extend(self.css_values('line-opacity', summary['line-opacity'])[1])
        stylesheet.extend(self.css_values('point-width', summary['point-width'])[1])
        stylesheet.extend(self.css_values(None, summary['labels'])[1])
        stylesheet = ''.join(stylesheet)

        palettes = ''
        if palette1:
            palettes += open('assets/{pal}.casc'.format(pal=palette1)).read()
        if palette2 and palette2 != palette1:
            palettes += open('assets/{pal}.casc'.format(pal=palette2)).read()

        stylesheet = """
{palettes}

Layer {{
    line-width: 1;
}}

{stylesheet}
    """.format(stylesheet=stylesheet, palettes=palettes)

        style = models.Style.objects.create(
            title=style_name,
            stylesheet=stylesheet
        )
        if existing_or_new == 'existing':
            layer = models.RenderedLayer.objects.get(slug=existing_layer_name)
            layer.styles.add(style)
        else:
            layer = models.RenderedLayer.objects.create(
                data_resource=models.DataResource.objects.get(slug=resource),
                default_style=style,
                title=new_layer_name,
                content=''
            )
            layer.styles_set.add(style)

        return HttpResponse('{{"url" : "/{redirect}?style={style}"}}'.format(
            redirect=layer.slug,
            style=style.slug
        ), mimetype='application/json')
