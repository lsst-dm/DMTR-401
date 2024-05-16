# Test script for LSST Data Management acceptance test campaign
# LVV-T1946:<https://jira.lsstcorp.org/secure/Tests.jspa#/testCase/LVV-T1946>
# LVV-T1946 tests verification element LVV-178, <https://jira.lsstcorp.org/browse/LVV-178>
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

def LVVT1947(instrument, tract, detector, visit, band, skymap):
    """ Execute test case LVV-T1947

    Parameters
    ----------
    tract: `int`
        Input tract for test.
    patch: `int`
        Input patch for test.
    band: `str`
        Band on which to test schema.
    """

    dataId = {'instrument':instrument, 'tract':tract, 'band':band,
              'detector':detector, 'visit':visit, 'skymap':skymap}
    print('Input dataId: ', dataId)

    try:
        obj_table = butler.get('diaObjectTable_tract', dataId = dataId)
    except:
        print('Invalid dataId. Please check and try again.')

    tractname = dataId['tract']
    print('\n-------------------------------------------------')
    print(f'\nChecking flux values for tract {tractname}, diaObjectTable_tract')
    check_flux_values(obj_table)


def check_flux_values(obj_table):
    """ Check that the flux values are within a range of reasonable
    values, and print the results to the screen

    Parameters
    ----------
    table: Source Table
        src table to check
    """

    bands = ['g', 'r', 'i', 'z', 'y']
    fluxes = ['psfFluxMAD', 'psfFluxMean',
              'scienceFluxMean',
              'psfFluxMin', 'psfFluxMax', 'psfFluxPercentile05',
              'psfFluxPercentile25', 'psfFluxPercentile50',
              'psfFluxPercentile75', 'psfFluxPercentile95',
              'psfFluxSigma', 'scienceFluxSigma']

    bright_maglim = -5.0*u.ABmag
    bright_fluxlim = bright_maglim.to(u.nJy)
    faint_fluxlim = -1e12*u.nJy

    for band in bands:
        print('\nflux column          % of bad flux values\n')
        for fluxcol_stub in fluxes:
            fluxcol = band+'_'+fluxcol_stub
            toofaint = (obj_table[fluxcol].values < faint_fluxlim.value)
            toobright = (obj_table[fluxcol].values > bright_fluxlim.value)
            fluxflag = (toofaint | toobright)
            bad_percentage = (np.sum(fluxflag)/len(fluxflag))*100*u.percent
            print(f'{fluxcol:20} {bad_percentage:7.2}')


if __name__ == "__main__":

    # Select an arbitrary source catalog from a deepCoadd:
    instrument = 'HSC'
    band = 'i'
    tract = 9697
    skymap = 'hsc_rings_v1'
    detector = 40
    visit = 36180

    # Run the test
    LVVT1947(instrument, tract, detector, visit, band, skymap)
