library(logging)
logLevel = Sys.getenv('PIMP_LOG_LEVEL', unset='WARNING')
logging::basicConfig(logLevel)
logger <- logging::getLogger('Pimp.runPimp', level=loglevels[logLevel])

loginfo('START OF R PIPELINE SCRIPT', logger=logger)
logger$info('Currently in %s', getwd())

getNeededString = function(name) {
    Sys.getenv(name, unset=NA)
}

getString = function(name, default) {
    Sys.getenv(name, unset=default)
}

getInteger = function(name, default) {
    value = getNeededString(name)
    if ( is.na(value) ) {
        return(default)
    }
    return(as.numeric(value))
}

args <- commandArgs(trailingOnly=TRUE)
analysis.id <- as.integer(args[1])
saveFixtures <- as.logical(args[2])
handler = getHandler('basic.stdout')
handler$formatter = function (record) {
    text <- paste(record$timestamp, paste(analysis.id, record$levelname, record$logger,
        record$msg, sep = ":"))
}

packratLibPath = file.path(getNeededString('PIMP_BASE_DIR'), '..', '..', 'packrat', 'lib', R.Version()$platform, paste(R.Version()$major, R.Version()$minor, sep="."))
logger$info('Setting library path to: %s', packratLibPath)
.libPaths(packratLibPath)

#envVariablesNames = c('PIMP_JAVA_PARAMETERS', 'PIMP_DATABASE_ENGINE', 'PIMP_DATABASE_NAME',
#	'PIMP_DATABASE_FILENAME', 'PIMP_DATABASE_USER', 'PIMP_DATABASE_PASSWORD', 'PIMP_DATABASE_HOST',
#	'PIMP_DATABASE_PORT')


#envVariables = Sys.getenv(envVariablesNames)

options(java.parameters=getString('PIMP_JAVA_PARAMETERS', paste("-Xmx",1024*8,"m",sep="")))

##need to setwd
loginfo('Analysis ID: %s', analysis.id, logger=logger)
if(is.na(analysis.id)) {
    stop("Analysis ID must be an integer.")
}


library(PiMPDB)
library(PiMP)

dbtype = getNeededString('PIMP_DATABASE_ENGINE')
if ( dbtype == 'django.db.backends.mysql' ) {
    DATABASE_TYPE = 'mysql'
    PIMP_DATABASE_NAME = getNeededString('MYSQL_DATABASE')
    PIMP_DATABASE_USER = getNeededString('MYSQL_USER')
        PIMP_DATABASE_PASSWORD = getNeededString('MYSQL_PASSWORD')
} else if ( dbtype == 'django.db.backends.sqlite3' ) {
    DATABASE_TYPE = 'sqlite'
    PIMP_DATABASE_NAME = file.path(getNeededString('PIMP_BASE_DIR'), getNeededString('SQLITE_DATABASE_FILENAME'))
    PIMP_DATABASE_USER = ''
        PIMP_DATABASE_PASSWORD = ''
} else {
    stop(paste('The database type', dbtype, 'is not recognised'))
}

db <- new("PiMPDB",
    dbuser=PIMP_DATABASE_USER,
    dbpassword=PIMP_DATABASE_PASSWORD,
    dbname=PIMP_DATABASE_NAME,
    dbhost=getString('PIMP_DATABASE_HOST', ''),
    dbport=getInteger('PIMP_DATABASE_PORT', 0),
    dbtype=DATABASE_TYPE
    )

#db <- new("PiMPDB", dbname="~/Downloads/sqlite3.db", dbtype="sqlite")
#db <- new("PiMPDB", dbuser=db.settings$user, dbpassword=db.settings$password, dbname="pimp_prod", dbhost=db.settings$host, dbtype=db.settings$type)

logger$info('DATABASE_NAME: %s', PIMP_DATABASE_NAME)
logger$info('DATABASE_TYPE: %s', DATABASE_TYPE)

experiment.id <- getExperimentID(db, analysis.id)
project.id <- getProjectID(db, analysis.id)

loginfo('experiment.id: %s', experiment.id, logger=logger)
loginfo('project.id: %s', project.id, logger=logger)

DATA_DIR = file.path(getString('PIMP_MEDIA_ROOT', file.path(getNeededString('PIMP_BASE_DIR'), '..', 'pimp_data')), 'projects')
loginfo('Data dir: %s', DATA_DIR, logger=logger)

PROJECT_DIR = file.path(DATA_DIR, project.id)
loginfo('Project dir: %s', PROJECT_DIR, logger=logger)
setwd(PROJECT_DIR)

experiment.samples <- getExperimentSamples(db, experiment.id)
experiment.groups <- getExperimentGroups(db, experiment.id)

samples <- getExperimentSamples(db, experiment.id)
controls <- getExperimentControls(db, experiment.id)
experiment.contrasts <- getExperimentComparisons(db, experiment.id)
# experiment.factors <- getExperimentGroups(db, experiment.id)
# experiment.levels <- getExperimentGroupMembers(db, experiment.factors$id)
analysis.params <- getAnalysisParameters(db, analysis.id)

##files
files <- list()
files$positive <- file.path("samples", "POS", samples$name)
files$negative <- file.path("samples", "NEG", samples$name)

##QCs
blank.idx <- which(controls$type=="blank")
blank.pos <- file.path("calibration_samples", "POS", controls$name[blank.idx])
blank.neg <- file.path("calibration_samples", "NEG", controls$name[blank.idx])

files$positive <- c(files$positive, blank.pos)
files$negative <- c(files$negative, blank.neg)

stds.idx <- which(controls$type=="standard")
stds <- file.path("calibration_samples", "standard", controls$name[stds.idx])

##build groups list
groups <- list()
for(i in 1:nrow(experiment.groups)) {
    members <- getExperimentGroupMembers(db, experiment.groups$id[i], experiment.id)
    for(j in 1:nrow(members)) {
        samples <- getMemberSamples(db, members$id[j])
        groups[[members$name[j]]] <- file_path_sans_ext(samples$name)
    }
}

if(length(blank.idx) > 0) {
    groups$Blank <- file_path_sans_ext(controls$name[blank.idx])
}

#comparisons
fetchedContrasts <- experiment.contrasts$contrast
loginfo('Number of fetchedContrasts: %d', length(fetchedContrasts), logger=logger)
loginfo('fetchedContrasts %s', fetchedContrasts, logger=logger)
controls <- experiment.contrasts$control
names <- experiment.contrasts$name
contrasts = c()
for ( i in 1:length(fetchedContrasts) ) {
    con = unlist(strsplit(controls[i], ','))
    if ( con[1] == '1' ) {
        cont = unlist(strsplit(fetchedContrasts[i], ','))
        fetchedContrasts[i] = paste0(cont[2], ',', cont[1])
    }
    contrasts = append(contrasts, fetchedContrasts[i])
}
loginfo('Number of contrasts: %d', length(contrasts), logger=logger)
loginfo('contrasts: %s', contrasts, logger=logger)
databases <- getAnnotationDatabases(db, analysis.id)
loginfo('databases: %s', databases, logger=logger)
pimp.params = getDefaultSettings()

loginfo('---------------------------------------------------', logger=logger)
loginfo('Preset Analysis parameters', logger=logger)
loginfo('---------------------------------------------------', logger=logger)
loginfo('mzmatch.filters names: %s', names(pimp.params$mzmatch.filters), logger=logger)
loginfo('mzmatch.filters: %s', pimp.params$mzmatch.filters, logger=logger)

param.idx <- which(analysis.params$state==1 | analysis.params$state==0)
if(length(param.idx) > 0) {
    params <- analysis.params[param.idx,]
    loginfo('Setting params', logger=logger)

    for(i in 1:nrow(params)) {
        logdebug('Name: %s Value: %s', params$name[i], params$value[i], logger=logger)

      if (params$state[i] == 1) {

        if(params$name[i]=="ppm") {
          pimp.params$xcms.params$ppm <- params$value[i]
          pimp.params$mzmatch.params$ppm <- params$value[i]
        }
        else if(params$name[i]=="rt.alignment") {
          pimp.params$mzmatch.params$rt.alignment <- "obiwarp"
        }
        else if(params$name[i]=="rtwindow") {
          pimp.params$mzmatch.params$id.rtwindow <- params$value[i]
        }
        else {
            if(is.na(params$value[i])){
              pimp.params$mzmatch.params[[params$name[i]]] <- TRUE
            }
            else {
              pimp.params$mzmatch.params[[params$name[i]]] <- params$value[i]
            }

        }
      }
      pimp.params$mzmatch.filters[[params$name[i]]] = as.logical(params$state[i])
    }
}

nSlaves = getInteger('PIMP_PIPELINE_NSLAVES', ifelse(length(unlist(groups)) >= 20, 20, length(unlist(groups))))

loginfo('---------------------------------------------------', logger=logger)
loginfo('Analysis parameters', logger=logger)
loginfo('---------------------------------------------------', logger=logger)
loginfo('files: %s', files, logger=logger)
loginfo('groups: %s', groups, logger=logger)
loginfo('stds: %s', stds, logger=logger)
loginfo('names: %s', names, logger=logger)
loginfo('contrasts: %s', contrasts, logger=logger)
loginfo('databases: %s', databases, logger=logger)
loginfo('nSlaves: %s', nSlaves, logger=logger)
loginfo('analysis.id: %d', analysis.id, logger=logger)
loginfo('mzmatch.params: %s', pimp.params$mzmatch.params, logger=logger)
loginfo('xcms.params: %s', pimp.params$xcms.params, logger=logger)
loginfo('peakml.params: %s', pimp.params$peakml.params, logger=logger)
loginfo('mzmatch.filters names: %s', names(pimp.params$mzmatch.filters), logger=logger)
loginfo('mzmatch.filters: %s', pimp.params$mzmatch.filters, logger=logger)

Pimp.runPipeline(files=files, groups=groups, comparisonNames=names, contrasts=contrasts, standards=stds, 
    databases=databases, nSlaves=nSlaves, reports="xml",
    db=db, mzmatch.params=pimp.params$mzmatch.params, mzmatch.filters=pimp.params$mzmatch.filters,
    mzmatch.outputs=pimp.params$mzmatch.outputs, xcms.params=pimp.params$xcms.params,
    peakml.params=pimp.params$peakml.params, analysis.id=analysis.id, saveFixtures=saveFixtures)

loginfo('END OF R PIPELINE SCRIPT', logger=logger)
quit(save = "default", status = 0, runLast = TRUE)
