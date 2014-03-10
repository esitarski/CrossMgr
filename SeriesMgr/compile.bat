
copy ..\Model.py .
copy ..\rsonlite.py .
copy ..\Checklist.py .
copy ..\Utils.py .
copy ..\GpxParse.py .
copy ..\GeoAnimation.py .
copy ..\Animation.py .
copy ..\GanttChart.py .
copy ..\ariel10.py .
copy ..\FitSheetWrapper.py .
copy ..\ReadSignOnSheet.py .
copy ..\ReadCategoriesFromExcel.py .
copy ..\ReadPropertiesFromExcel.py .

python -mcompileall -l .
python SeriesMgrSetup.py py2exe

SET /P RESULT=[Press any key to continue...]