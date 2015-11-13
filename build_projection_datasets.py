import sys

if len(sys.argv) < 3:
	print ''
	print 'please provide a working directory & output file name, e.g.'
	print ''
	print '   build_projection_datasets.py data/ pms.pickle'
	print ''
	sys.exit(1)

import os

os.chdir(sys.argv[1])

from allensdk.core.mouse_connectivity_cache import MouseConnectivityCache
from allensdk.api.queries.ontologies_api import OntologiesApi

mcc = MouseConnectivityCache(manifest_file='mcc_manifest.json')
all_experiments = mcc.get_experiments(dataframe=True)

ontology = mcc.get_ontology()

summary_structures = OntologiesApi().get_structures(
	structure_set_names='Mouse Connectivity - Summary')
summary_structure_ids = [s['id'] for s in summary_structures]

print 'build dict of injection structure id to experiment list'
ist2e = {}
for eid in all_experiments.index:
    for ist in all_experiments.ix[eid]['injection-structures']:
        isti = ist['id']
        if isti not in ist2e:
            ist2e[isti] = []
        ist2e[isti].append(eid)

# this may hours to days to run depending on bandwidth
print 'obtain projection maps per injection site'
pms = {}
for isti, elist in ist2e.items():
    pms[isti] = mcc.get_projection_matrix(
        experiment_ids=elist,
        projection_structure_ids=summary_structure_ids,
        parameter='projection_density')
    print 'injection site id', isti, ' has ', len(elist), ' experiments with pm shape ', pms[isti]['matrix'].shape  

print 'save projection maps to ' + os.path.join([sys.argv[1], sys.argv[2]])
import cPickle as p
with open(sys.argv[2], 'w') as fd:
	p.dump(pms, fd)
