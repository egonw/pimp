frankMSnPeakMatrix <- function (source_directory){

  ########################## JOE WANDY'S SCRIPT #######################  
  require(xcms)
  require(Hmisc)
  require(gtools)
  print('In MSN peak matrix')
  # Ensure the source directory is a valid filename
  if(!file.exists(source_directory)){
  return (warning('Invalid filename supplied'))
  }

  # Do peak detection using CentWave

    peak_detection_method = "centWave"
    resolution_ppm = 2
    signal_to_noise_threshold = 3
    peak_width = c(5,100)
    prefilter_param = c(3,1000)
    mz_differential = 0.001
    integration = 0
    gaussian_fit = FALSE
    verbose_column = TRUE

      xset <- xcmsSet(files=source_directory, method=peak_detection_method, ppm=resolution_ppm,
                      snthresh=signal_to_noise_threshold, peakwidth=peak_width,
                      prefilter=prefilter_param, mzdiff=mz_differential, integrate=integration,
                      fitgauss=gaussian_fit, verbose.column=verbose_column)
      xset <- group(xset)


        print ('no MS1 peaks')
      # When the script is called in Frank, the working directory is where the script is called from
      # which is ../pimp/django_projects/pimp
      # so the additional folders in frank must be concatinated to source the file
      source(paste(getwd(), '/frank/Frank_R/frankXcmsSetFragments.R', sep=""))
      frags <- frankXcmsSetFragments(xset, cdf.corrected = FALSE, min.rel.int=0.01, max.frags = 5000,
                                msnSelect=c("precursor_int"), specFilter=c("specPeaks"), match.ppm=7,
                                sn=3, mzgap=0.005, min.r=0.75, min.diff=10)



  ## Label the peaks with the source file they were derived from ###
  peaks <- as.data.frame(frags@peaks)
  sourcefiles <- basename(xset@filepaths)
  sampleList <- peaks[, 'Sample']
  sourcePeakList <- factor(sampleList, labels = sourcefiles)
  peaks[, "SourceFile"] <- sourcePeakList
  print (head(peaks))
  return (peaks)
}