import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pimp.settings_dev')

import django
django.setup()

from experiments.models import DefaultParameter, Database
from frank.models import AnnotationTool, ExperimentalProtocol, AnnotationToolProtocols

def populate():
    iqr_parameter = add_default_parameter(
        name = "iqr",
        value = 0.5,
        state = True,
    )

    rsd_parameter = add_default_parameter(
        name = "rsd",
        value = 0.5,
        state = True,
    )

    noise_parameter = add_default_parameter(
        name = "noise",
        value = 0.8,
        state = True,
    )

    ppm_parameter = add_default_parameter(
        name = "ppm",
        value = 3,
        state = True,
    )

    min_detection = add_default_parameter(
        name = "mindetection",
        value = 3,
        state = True,
    )

    min_intensity = add_default_parameter(
        name = "minintensity",
        value = 5000,
        state = True,
    )

    rt_window = add_default_parameter(
        name = "rtwindow",
        value = 0.05,
        state = True,
    )

    rt_alignment = add_default_parameter(
        name = "rt.alignment",
        value = None,
        state = True,
    )

    normalization = add_default_parameter(
        name = "normalization",
        value = None,
        state = False,
    )

    kegg_db = add_database(
        name = "kegg"
    )

    kegg_db = add_database(
        name = "hmdb"
    )

    kegg_db = add_database(
        name = "lipidmaps"
    )

    mass_bank_annotation_tool = add_annotation_tool(
        name = 'MassBank'
    )

    NIST_annotation_tool = add_annotation_tool(
        name = 'NIST'
    )

    network_sampler_annotation_tool = add_annotation_tool(
        name = 'LCMS DDA Network Sampler'
    )

    lcms_dda_experimental_protocol = add_experimental_protocol(
        name = 'Liquid-Chromatography Mass-Spectroscopy Data-Dependent Acquisition'
    )

    gcms_dia_experimental_protocol = add_experimental_protocol(
        name = 'Gas-Chromatography Mass-Spectroscopy Electron Impact Ionisation'
    )

    lcms_dia_experimental_protocol = add_experimental_protocol(
        name = 'Liquid-Chromatography Data-Independent Acquisition'
    )

    mass_bank_protocols = add_annotation_tool_protocols(
        [lcms_dda_experimental_protocol,gcms_dia_experimental_protocol],
        mass_bank_annotation_tool
    )

    NIST_protocols = add_annotation_tool_protocols(
        [lcms_dda_experimental_protocol,gcms_dia_experimental_protocol],
        NIST_annotation_tool
    )

    network_sampler_annotation_tool = add_annotation_tool_protocols(
        [lcms_dda_experimental_protocol],
        network_sampler_annotation_tool
    )



def add_default_parameter(name, value, state):
    parameter = DefaultParameter.objects.get_or_create(
        name = name,
        value = value,
        state = state,
    )[0]
    print 'Creating default parameter - '+name+'...'
    parameter.save()
    return parameter

def add_database(name):
    database = Database.objects.get_or_create(
       name = name,
    )[0]
    print 'Creating default database - '+name+'...'
    database.save()
    return database

def add_annotation_tool(name):
    annotation_tool = AnnotationTool.objects.get_or_create(
       name = name,
    )[0]
    print 'Creating default annotation tool - '+name+'...'
    annotation_tool.save()
    return annotation_tool

def add_experimental_protocol(name):
    experimental_protocol = ExperimentalProtocol.objects.get_or_create(
       name = name,
    )[0]
    print 'Creating experimental protocol - '+name+'...'
    experimental_protocol.save()
    return experimental_protocol

def add_annotation_tool_protocols(protocols_list, annotation_tool):
    for protocol in protocols_list:
        print 'Adding '+protocol.name+' to Annotation Tool '+annotation_tool.name
        annotation_tool_protocol = AnnotationToolProtocols.objects.get_or_create(
            annotation_tool = annotation_tool,
            experimental_protocol = protocol
        )

# Execution starts here
if __name__=='__main__':
    print "Populating default parameters..."
    populate()