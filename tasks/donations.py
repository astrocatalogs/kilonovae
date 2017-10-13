"""Import tasks for data directly donated to the Open Supernova Catalog."""
import csv
import json
import os
from math import floor

from astrocats.catalog.spectrum import SPECTRUM
from astrocats.catalog.utils import get_sig_digits, pbar, round_sig
from astropy.time import Time as astrotime


def do_donated_photo(catalog):
    """Import donated photometry."""
    # task_str = catalog.get_current_task_str()

    # Private donations here #
    if not catalog.args.travis:
        pass
    # End private donations #

    catalog.journal_entries()
    return


def do_donated_spectra(catalog):
    """Import donated spectra."""
    task_str = catalog.get_current_task_str()
    fpath = os.path.join(catalog.get_current_task_repo(), 'Donations')
    with open(os.path.join(fpath, 'meta.json'), 'r') as f:
        metadict = json.loads(f.read())

    donationscnt = 0
    oldname = ''
    for fname in pbar(metadict, task_str):
        name = metadict[fname]['name']
        name = catalog.get_preferred_name(name)
        if oldname and name != oldname:
            catalog.journal_entries()
        oldname = name
        if 'bibcode' in metadict[fname]:
            sec_bibc = metadict[fname]['bibcode']
            name, source = catalog.new_entry(name, bibcode=sec_bibc)
        else:
            sec_srcn = metadict[fname]['srcname']
            name, source = catalog.new_entry(name, srcname=sec_srcn)

        date = metadict[fname].get('date', '')
        year, month, day = date.split('/')
        sig = get_sig_digits(day) + 5
        day_fmt = str(floor(float(day))).zfill(2)
        time = astrotime(year + '-' + month + '-' + day_fmt).mjd
        time = time + float(day) - floor(float(day))
        time = round_sig(time, sig=sig)
        print(time)

        with open(os.path.join(fpath, fname), 'r') as f:
            specdata = list(
                csv.reader(
                    f, delimiter=' ', skipinitialspace=True))
            specdata = list(filter(None, specdata))
            newspec = []
            oldval = ''
            for row in specdata:
                if row[0][0] == '#':
                    continue
                if row[1] == oldval:
                    continue
                newspec.append(row)
                oldval = row[1]
            specdata = newspec
        haserrors = len(specdata[0]) == 3 and specdata[0][2] and specdata[0][
            2] != 'NaN'
        specdata = [list(i) for i in zip(*specdata)]

        wavelengths = specdata[0]
        fluxes = specdata[1]
        errors = ''
        if haserrors:
            errors = specdata[2]

        specdict = {
            SPECTRUM.U_WAVELENGTHS: 'Angstrom',
            SPECTRUM.U_TIME: 'MJD',
            SPECTRUM.TIME: time,
            SPECTRUM.WAVELENGTHS: wavelengths,
            SPECTRUM.FLUXES: fluxes,
            SPECTRUM.ERRORS: errors,
            SPECTRUM.SOURCE: source,
            SPECTRUM.FILENAME: fname
        }
        if 'instrument' in metadict[fname]:
            specdict[SPECTRUM.INSTRUMENT] = metadict[fname]['instrument']
        if 'telescope' in metadict[fname]:
            specdict[SPECTRUM.TELESCOPE] = metadict[fname]['telescope']
        if 'observer' in metadict[fname]:
            specdict[SPECTRUM.OBSERVER] = metadict[fname]['observer']
        if 'yunit' in metadict[fname]:
            specdict[SPECTRUM.U_FLUXES] = metadict[fname]['yunit']
            specdict[SPECTRUM.U_ERRORS] = metadict[fname]['yunit']
        else:
            if max([float(x) for x in fluxes]) < 1.0e-5:
                fluxunit = 'erg/s/cm^2/Angstrom'
            else:
                fluxunit = 'Uncalibrated'
            specdict[SPECTRUM.U_FLUXES] = fluxunit
            specdict[SPECTRUM.U_ERRORS] = fluxunit
        catalog.entries[name].add_spectrum(**specdict)
        donationscnt = donationscnt + 1
        if (catalog.args.travis and
                donationscnt % catalog.TRAVIS_QUERY_LIMIT == 0):
            break

    catalog.journal_entries()
    return
