for i in libs/*.jar ; do
	j=$(basename $i .jar)
	base=${j%-*}
	vers=${j##*-}
	echo base=$base vers=$vers
	mvn install:install-file -DlocalRepositoryPath=repo -DcreateChecksum=true -Dpackaging=jar \
		-Dfile=$i  -DgroupId=libs -DartifactId=$base -Dversion=$vers 
done
