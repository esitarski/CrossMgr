import pstats
p = pstats.Stats('CrossMgr.prof')
p.sort_stats('cumulative').print_stats(20)
p.sort_stats('time').print_stats(20)
p.sort_stats('calls').print_stats(20)