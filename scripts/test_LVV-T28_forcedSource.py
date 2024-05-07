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

def LVVT28(instrument, tract, patch, band, skymap):
    """ Execute test case LVV-T28

    Parameters
    ----------
    instrument: `str`
        Instrument from which the data is derived
    tract: `int`
        Input tract for test.
    patch: `int`
        Input patch for test.
    band: `str`
        Band on which to test schema.
    """

    dataIdCoadd = {'instrument':instrument, 'tract':tract, 'band':band,
                   'patch':patch, 'skymap':skymap}
    print('Input dataId: ', dataIdCoadd)

    print('\nChecking parquet forcedSourceTable:')
    try:
        srctable = butler.get('forcedSourceTable', dataId = dataIdCoadd)
    except:
        print('Invalid dataId. Please check and try again.')

    patchname = dataIdCoadd['patch']
    print(f'\nChecking flux values for patch {patchname}\n')
    check_flux_values(srctable)


def check_flux_values(src_table):
    """ Check that the flux values are within a range of reasonable
    values, and print the results to the screen

    Parameters
    ----------
    table: forcedSource Table
        forcedSrc table to check
    """

    flux_columns = ['psfFlux', 'psfDiffFlux']

    bright_maglim = -5.0*u.ABmag
    bright_fluxlim = bright_maglim.to(u.nJy)
    faint_fluxlim = -1e6*u.nJy

    # Flags to apply for all flux columns:
    okisprimary = src_table['detect_isPrimary'] == 0
    okfluxflag = (src_table["psfFlux_flag"] == 0) | (src_table['psfDiffFlux_flag'] == 0)
    okpixflags = src_table['pixelFlags_saturatedCenter'] == 0

    print('\nflux column          % of bad flux values\n')
    for fluxcol in flux_columns:
        toofaint = (src_table[fluxcol].values < faint_fluxlim.value)
        toobright = (src_table[fluxcol].values > bright_fluxlim.value)
        fluxflag = (toofaint | toobright) & okisprimary & okfluxflag & okpixflags
        bad_percentage = (np.sum(fluxflag)/len(fluxflag))*100*u.percent
        print(f'{fluxcol:20} {bad_percentage:7.2}')


if __name__ == "__main__":

    # Select an arbitrary source catalog from a deepCoadd:
    instrument = 'HSC'
    band = 'i'
    tract = 9697
    patch = 13
    skymap = 'hsc_rings_v1'

    # Run the test
    LVVT28(instrument, tract, patch, band, skymap)

