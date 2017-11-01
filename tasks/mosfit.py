"""Import tasks related to MOSFiT."""
import os
from glob import glob

import dropbox

from astrocats.catalog.utils import pbar
from astrocats.kilonovae.kilonova import Kilonova, KILONOVA
from astrocats.catalog.photometry import PHOTOMETRY


def do_mosfit(catalog):
    """Import models produced by MOSFiT from Dropbox."""
    REALIZATION_LIMIT = 10

    task_str = catalog.get_current_task_str()
    try:
        with open('mosfit.key', 'r') as f:
            mosfitkey = f.read().splitlines()[0]
    except Exception:
        catalog.log.warning('MOSFiT key not found, make sure a file named '
                            '`mosfit.key` containing the key is placed the '
                            'astrocats directory.')
        mosfitkey = ''

    # Get new data from Dropbox.
    dbx = dropbox.Dropbox(mosfitkey)
    files = list(sorted([
        x.name for x in dbx.files_list_folder('').entries
        if not x.name.startswith('.')
    ]))
    fdir = os.path.join(catalog.get_current_task_repo(), 'MOSFiT')
    if not os.path.isdir(fdir):
        os.mkdir(fdir)
    old_name = ''
    for fname in pbar(files, desc=task_str):
        fpath = os.path.join(fdir, fname)

        if 'GW' not in fpath:
            continue

        if not os.path.isfile(fpath):
            md, res = dbx.files_download('/' + fname)
            jtxt = res.content
            with open(fpath, 'wb') as f:
                f.write(jtxt)

    # Load data in models folder.
    efiles = [x.split('/')[-1] for x in glob(os.path.join(fdir, '*'))]
    for fname in efiles:
        fpath = os.path.join(fdir, fname)
        new_entry = Kilonova.init_from_file(
            catalog, path=fpath, compare_to_existing=False, try_gzip=True,
            clean=False, merge=False, filter_on={
                'realization': [str(x) for x in range(1, REALIZATION_LIMIT)]})

        name = new_entry[KILONOVA.NAME]

        aliases = new_entry.get_aliases()

        if not any([x.startswith('GW') for x in aliases]):
            os.remove(fpath)
            continue

        # Only take a number of realizations up to the realization limit.
        new_photo = []
        for photo in new_entry[KILONOVA.PHOTOMETRY]:
            real = int(photo.get(PHOTOMETRY.REALIZATION, -1))
            if real < 0 or real >= REALIZATION_LIMIT:
                continue
            new_photo.append(photo)
        new_entry[KILONOVA.PHOTOMETRY] = new_photo

        old_entry = None
        if name in catalog.entries:
            if catalog.entries[name]._stub:
                old_entry = Kilonova.init_from_file(
                    catalog, name=name, compare_to_existing=False)
            else:
                old_entry = catalog.entries[name]

        if old_entry:
            catalog.copy_entry_to_entry(new_entry, old_entry,
                                        compare_to_existing=False)
            catalog.entries[name] = old_entry
        else:
            catalog.entries[name] = new_entry

        if old_name != name:
            catalog.journal_entries()
        old_name = name

    return
