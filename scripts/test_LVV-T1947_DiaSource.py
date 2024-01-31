# Test script for LSST Data Management acceptance test campaign
# LVV-T28:<https://jira.lsstcorp.org/secure/Tests.jspa#/testCase/LVV-T28>
# LVV-T28 tests verification element LVV-178, <https://jira.lsstcorp.org/browse/LVV-178>
# which verifies requirement DMS-REQ-0347-V-01: Measurements in catalogs
#
# The lsst environment must be set up to run this test,
# see <https://pipelines.lsst.io/install/setup.html> for more details

import os
import numpy as np
import astropy.units as u

from lsst.daf.butler import Butler

# Confirm the version of the Science Pipelines:
os.system('eups list -s | grep lsst_distrib')

# For RC2 data on the USDF:
config = '/repo/main'
collection = 'HSC/runs/RC2/w_2023_39/DM-40985'
butler = Butler(config, collections=collection)

def LVVT1947(instrument, visit, detector):
    """ Execute test case LVV-T1947

    Parameters
    ----------
    instrument: `str`
        Instrument from which the data is derived
    visit: `int`
        Input visit for test
    detector: `int`
        Detector on which to test schema
    """

    dataId = {'instrument':instrument, 'visit':visit, 'detector':detector}
    print('Input dataId: ', dataId)

    try:
        src = butler.get('goodSeeingDiff_diaSrc', dataId = dataId)
    except:
        print('Invalid dataId. Please check and try again.')

    print('Checking goodSeeingDiff_diaSrc...\n')
    sch = src.schema
    src_flag = check_schema(sch)

    # If any of the units are not "count," print "FALSE."
    assert(np.all(src_flag)), 'FALSE: not all instFlux entries have units of counts.'
    
    # If all of the flux units are "count," print "TRUE."
    print('\n All src table instFlux entries have units of counts: ', np.all(src_flag))

    # Add skymap to the dataId for forced_source_on_diaobject:
    dataId['skymap'] = 'hsc_rings_v1'
    dataId['tract'] = 9697

    try:
        src = butler.get('forced_src_diaObject', dataId = dataId)
    except:
        print('Invalid dataId. Please check and try again.')

    print('\nChecking forced_src_diaObject...\n')
    sch = src.schema
    src_flag = check_schema(sch)

    # If any of the units are not "count," print "FALSE."
    assert(np.all(src_flag)), 'FALSE: not all instFlux entries have units of counts.'
    
    # If all of the flux units are "count," print "TRUE."
    print('\n All src table instFlux entries have units of counts: ', np.all(src_flag))


    try:
        srctable = butler.get('diaSourceTable', dataId = dataId)
    except:
        print('Invalid dataId. Please check and try again.')

    visitname = dataId['visit']
    print(f'\nChecking flux values for visit {visitname}\n')
    check_flux_values(srctable)


def check_flux_values(src_table):
    """ Check that the flux values are within a range of reasonable
    values, and print the results to the screen

    Parameters
    ----------
    table: Source Table
        src table to check
    """

    flux_columns = ['apFlux', 'psfFlux', 'scienceFlux', 'dipoleMeanFlux']

    bright_maglim = -5.0*u.ABmag
    bright_fluxlim = bright_maglim.to(u.nJy)
    faint_fluxlim = -1e6*u.nJy

    # Flags to apply for all flux columns:
    okflag = (src_table["pixelFlags_bad"] == 0) &\
             (src_table["pixelFlags_suspect"] == 0) &\
             (src_table["pixelFlags_saturatedCenter"] == 0) &\
             (src_table["pixelFlags_interpolated"] == 0) &\
             (src_table["pixelFlags_interpolatedCenter"] == 0) &\
             (src_table["pixelFlags_edge"] == 0)

    print('flux column          % of bad flux values\n')
    for fluxcol in flux_columns:
        toofaint = (src_table[fluxcol].values < faint_fluxlim.value)
        toobright = (src_table[fluxcol].values > bright_fluxlim.value)
        if (fluxcol == 'scienceFlux'):
            okfluxflag = src_table['psfFlux_flag'] == 0
        elif (fluxcol == 'trailFlux'):
            okfluxflag = src_table['shape_flag'] == 0
        elif (fluxcol == 'dipoleMeanFlux'):
            okfluxflag = src_table['psfFlux_flag'] == 0
        else:
            okfluxflag = src_table[fluxcol+'_flag'] == 0
        fluxflag = (toofaint | toobright) & okflag
        bad_percentage = (np.sum(fluxflag)/len(fluxflag))*100*u.percent
        print(f'{fluxcol:20} {bad_percentage:7.2}')


def check_schema(sch):
    """ Check the units on each flux entry in the schema

    Parameters
    ----------
    sch: Schema 
        src catalog schema to check

    Returns
    -------
    src_flag: `list` of `bool`
        Boolean list containing "True" for elements with flux units in "count"
    """

    src_flag = []
    for entry in sch:
        field = entry.getField().getName()
        if 'instFlux' in field and 'flag' not in field and 'Cov' not in field:
            flux_units = entry.getField().getUnits()
            src_flag.append('count' in flux_units)
            print(f'{field}..... {flux_units:20}')
    return src_flag


if __name__ == "__main__":

    # Select an arbitrary source catalog from a difference image:
    instrument = 'HSC'
    detector = 40
    visit = 36180

    # Run the test
    LVVT1947(instrument, visit, detector)
