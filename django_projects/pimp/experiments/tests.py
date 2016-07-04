from datetime import datetime
import os
import shutil
from test.test_support import EnvironmentVarGuard

from django.db import transaction
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.testcases import TransactionTestCase

from mock.mock import patch

from experiments.models import Analysis, Experiment, DefaultParameter, Params, \
    Parameter, Database, Comparison, AttributeComparison
from experiments.tasks import start_pimp_pipeline
from fileupload.models import ProjFile, Picture, SampleFileGroup, Sample, \
    StandardFileGroup, CalibrationSample
from groups.models import Group, Attribute, ProjfileAttribute, SampleAttribute
import populate_pimp as population_script
from projects.models import Project

def populate_database(xml_file_path):
    print 'populating database from %s' % xml_file_path
    
def save_analysis():
    print 'Saving analysis'

def create_test_user():
    try:
        user = User.objects.get_by_natural_key('testrunner')
    except ObjectDoesNotExist:
        user = User.objects.create_user(
            username='testrunner',
            email='testrunner@gmail.com',
            password='password'
        )
    return user

def create_sample(project, fixture_dir, name):
        
    name = '%s.mzXML' % name
    f = file('%s/samples/POS/%s' % (fixture_dir, name), 'rb') 
    file_pos = Picture.objects.create(
        project = project,
        file = SimpleUploadedFile('%s' % name, f.read()),
        name = '%s' % name,
    )
    file_pos.setpolarity('+')

    f = file('%s/samples/NEG/%s' % (fixture_dir, name), 'rb') 
    file_neg = Picture.objects.create(
        project = project,
        file = SimpleUploadedFile('%s' % name, f.read()),
        name = '%s' % name,
    )
    file_neg.setpolarity('-')
     
    samplefilegroup = SampleFileGroup.objects.create(type="mzxml", posdata=file_pos, negdata=file_neg)
    samplefilegroup.save()        
 
    sample = Sample.objects.create(project=project,name=name, samplefile=samplefilegroup)
    sample.save() 

    return sample
    
def create_calibration_sample(project, fixture_dir, name):

    name = '%s.mzXML' % name
    f = file('%s/calibration_samples/POS/%s' % (fixture_dir, name), 'rb') 
    file_pos = ProjFile.objects.create(
        project = project,
        file = SimpleUploadedFile('%s' % name, f.read()),
        name = '%s.mzXML' % name
    )
    file_pos.setpolarity('+')

    f = file('%s/calibration_samples/NEG/%s' % (fixture_dir, name), 'rb') 
    file_neg = ProjFile.objects.create(
        project = project,
        file = SimpleUploadedFile('%s' % name, f.read()),
        name = '%s' % name
    )
    file_neg.setpolarity('-')

    standardfilegroup = StandardFileGroup.objects.create(type="mzxml", posdata=file_pos, negdata=file_neg)
    standardfilegroup.save()

    sample = CalibrationSample.objects.create(project=project, name=name, standardFile=standardfilegroup)
    sample.save() 
    
    return sample
    
def create_standard_csv(project, fixture_dir, name):

    name = '%s.csv' % name
    f = file('%s/calibration_samples/standard/%s' % (fixture_dir, name), 'rb') 
    file_std = ProjFile.objects.create(
        project = project,
        file = SimpleUploadedFile('%s' % name, f.read()),
        name = '%s' % name
    )
    file_std.setpolarity('std')

    standardfilegroup = StandardFileGroup.objects.create(type="toxid", data=file_std)
    standardfilegroup.save()

    sample = CalibrationSample.objects.create(project=project, name=name, standardFile=standardfilegroup)
    sample.save()
    
    return sample 

def create_grouping(group_name, attribute_list):
    
    group = Group.objects.create(name=group_name)
    group.save()
    
    attr_map = {}
    for attr in attribute_list:
        attr_map[attr] = Attribute.objects.create(name=attr, group=group)
        attr_map[attr].save()
        
    return attr_map

def group_calibration_samples(qc_list, blank_list, std_list):

    # don't change the group and the attribute names, seems to be hardcoded !?!
    group_name = 'calibration_group'
    attribute_names = ['qc', 'blank', 'standard']
    calibration_types = create_grouping(group_name, attribute_names)

    qc_attr = calibration_types['qc']
    for qc_samp in qc_list:
        ProjfileAttribute.objects.create(attribute=qc_attr, calibrationsample=qc_samp)

    blank_attr = calibration_types['blank']
    for blank_samp in blank_list:
        ProjfileAttribute.objects.create(attribute=blank_attr, calibrationsample=blank_samp)        

    std_attr = calibration_types['standard']
    for std_samp in std_list:
        ProjfileAttribute.objects.create(attribute=std_attr, calibrationsample=std_samp)
    
def create_default_analysis_parameters():
    
    default_parameters = DefaultParameter.objects.all()
    params = Params()
    params.save()
    for default in default_parameters:
        parameter = Parameter(state=default.state, name=default.name, value=default.value)
        parameter.save()
        params.param.add(parameter)            
        
    databases_ids = Database.objects.all().exclude(name='standards').values_list('id', flat=True)
    for db_id in databases_ids:
        params.databases.add(db_id)

    return params

def create_analysis(experiment_title, user):
    
    params = create_default_analysis_parameters()    
    experiment = Experiment.objects.create(title=experiment_title)               
    analysis = Analysis.objects.create(
        owner = user.username,
        experiment = experiment,
        params = params,
        status = 'Ready'
    )
    
    analysis.save()
    return experiment, analysis

def compare(comparison_name, experiment, case, control):
    
    comparison = Comparison(name=comparison_name, experiment=experiment)
    comparison.save()
            
    attribute_comp = AttributeComparison(control=False, attribute=case, comparison=comparison)
    attribute_comp.save()

    attribute_comp = AttributeComparison(control=True, attribute=control, comparison=comparison)
    attribute_comp.save()

# Django's TestCase class wraps each test in a transaction and rolls back that transaction after each test, 
# in order to provide test isolation. This means that no transaction is ever actually committed, thus your 
# on_commit() callbacks will never be run. If you need to test the results of an on_commit() callback, use a 
# TransactionTestCase instead.
class ExperimentTestCase(TransactionTestCase):

    def setUp(self):

        basedir = settings.BASE_DIR
        population_script.populate(superpathway_filename=os.path.join(basedir, 'kegg_pathway_superPathway.csv'))

        # path to find the fixture data
        self.fixture_dir = os.path.join(basedir, 'fixtures/projects/1')                           

        # set the paths to upload and process the test data
        self.test_media_root = settings.MEDIA_ROOT + '_test'
        settings.MEDIA_ROOT = self.test_media_root 

        # for use in the R pipeline
        self.env = EnvironmentVarGuard() 
        self.env.set('PIMP_DATABASE_NAME', 'test_' + os.environ['PIMP_DATABASE_NAME'])
        self.env.set('PIMP_MEDIA_ROOT', self.test_media_root)
        
    @patch('experiments.tasks.populate_database')
    @patch('experiments.tasks.send_email')
    def test_analysis(self, mock_populate_database, mock_send_email):
        """test that R analysis pipeline can run"""
        
        #######################################################
        # 1. create user and project
        #######################################################

        user = create_test_user()
        project = Project.objects.create(
            title='test_project', 
            user_owner = user,
            description = 'test',
            created = datetime.now(),
            modified = datetime.now()
        )

        #######################################################
        # 2. create calibration, blank and std samples
        #######################################################

        samp_names = ['Beer_PoolB_full_f', 'Beer_PoolB_full_g', 'Beer_PoolB_full_h', 'Beer_PoolB_full_i']
        qc_list = []
        for name in samp_names:
            qc_list.append(create_calibration_sample(project, self.fixture_dir, name))

        samp_names = ['blank1', 'blank2', 'blank3', 'blank4']
        blank_list = []
        for name in samp_names:
            blank_list.append(create_calibration_sample(project, self.fixture_dir, name))

        samp_names = ['Std1_1_20150422_150810', 'Std2_1_20150422_150711', 'Std3_1_20150422_150553']
        std_list = []
        for name in samp_names:
            std_list.append(create_standard_csv(project, self.fixture_dir, name))
        
        #######################################################
        # 3. group the calibration samples by their attributes   
        #######################################################             

        group_calibration_samples(qc_list, blank_list, std_list)
        
        #######################################################
        # 4. create samples
        #######################################################
        
        beer1_1 = create_sample(project, self.fixture_dir, 'Beer_1_full1')
        beer1_2 = create_sample(project, self.fixture_dir, 'Beer_1_full2')
        beer1_3 = create_sample(project, self.fixture_dir, 'Beer_1_full3')

        beer2_1 = create_sample(project, self.fixture_dir, 'Beer_2_full1')
        beer2_2 = create_sample(project, self.fixture_dir, 'Beer_2_full2')
        beer2_3 = create_sample(project, self.fixture_dir, 'Beer_2_full3')

        beer3_1 = create_sample(project, self.fixture_dir, 'Beer_3_full1')
        beer3_2 = create_sample(project, self.fixture_dir, 'Beer_3_full2')
        beer3_3 = create_sample(project, self.fixture_dir, 'Beer_3_full3')
 
        beer4_1 = create_sample(project, self.fixture_dir, 'Beer_4_full1')
        beer4_2 = create_sample(project, self.fixture_dir, 'Beer_4_full2')
        beer4_3 = create_sample(project, self.fixture_dir, 'Beer_4_full3')

        #######################################################
        # 5. group the samples into conditions
        #######################################################
        
        group_name = 'test_experiment'
        attribute_names = ['beer1', 'beer2', 'beer3', 'beer4']
        conditions = create_grouping(group_name, attribute_names)
        
        beer1_attr = conditions['beer1']
        SampleAttribute.objects.create(attribute=beer1_attr, sample=beer1_1)        
        SampleAttribute.objects.create(attribute=beer1_attr, sample=beer1_2)        
        SampleAttribute.objects.create(attribute=beer1_attr, sample=beer1_3)        

        beer2_attr = conditions['beer2']
        SampleAttribute.objects.create(attribute=beer2_attr, sample=beer2_1)        
        SampleAttribute.objects.create(attribute=beer2_attr, sample=beer2_2)        
        SampleAttribute.objects.create(attribute=beer2_attr, sample=beer2_3)        
        
        beer3_attr = conditions['beer3']
        SampleAttribute.objects.create(attribute=beer3_attr, sample=beer3_1)        
        SampleAttribute.objects.create(attribute=beer3_attr, sample=beer3_2)        
        SampleAttribute.objects.create(attribute=beer3_attr, sample=beer3_3)        
  
        beer4_attr = conditions['beer4']
        SampleAttribute.objects.create(attribute=beer4_attr, sample=beer4_1)        
        SampleAttribute.objects.create(attribute=beer4_attr, sample=beer4_2)        
        SampleAttribute.objects.create(attribute=beer4_attr, sample=beer4_3)                

        #######################################################        
        # 6. create a new experiment and analysis
        #######################################################
        
        experiment, analysis = create_analysis('test_analysis', user)
        print experiment.id
        print analysis.id
        experiment.save()
        analysis.save()
                
        #######################################################                
        # 7. set up comparisons
        #######################################################

        compare('comparison_1', experiment, beer1_attr, beer2_attr)
        compare('comparison_2', experiment, beer3_attr, beer4_attr)

        #######################################################
        # 8. Run the R analysis pipeline
        #######################################################

        transaction.commit() # commit to the test db so it can be picked up by R
        success = False
        with self.env:
            print 'Using %s as database' % self.env['PIMP_DATABASE_NAME']
            success = start_pimp_pipeline(analysis, project, user)

        #######################################################
        # 9. Check the results from the R pipeline
        #######################################################

        # assert that the return code from R is 0
        self.assertEqual(success, True)        
        
        # assert that analysis status is set to Finished
        analysis = Analysis.objects.get_or_create(id=analysis.id)[0]
        self.assertEqual(analysis.status, 'Finished')
        
        # assert that populate database is called
        self.assertTrue(mock_populate_database.called)
        
        # assert that email is sent 
        self.assertTrue(mock_send_email.called)

        #######################################################
        # 10. remove the analysis results
        #######################################################
        
        shutil.rmtree(os.path.join(self.test_media_root, 'projects'))