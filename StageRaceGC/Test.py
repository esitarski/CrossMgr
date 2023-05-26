import os
import Model
from StageRaceGCToExcel import StageRaceGCToExcel

model, fname = Model.unitTest()
name, ext = os.path.splitext(fname)
fname_gc = name + '-GC' + ext
StageRaceGCToExcel( fname_gc, model )
