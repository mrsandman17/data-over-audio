Initial test (Home):
	Constant params:
		sync_repeat=2
		sample_rate=44100
		sync_freq=80
		sync_search_chunk=10000
		sync_freq_deviation=5
		min single_freq_duration = 0.5

	Tests:
		1. min freq_diff
		2. Volume effect
		4. min frequecy ranges
		
	Test results:
		1. 2 < freq_difference, min_frequency = 120. 
		2. Volume poses an important factor. The higher the volume, better reception (ability to transmit denser frequecies(low freq difference))
		4. 120 < min_frequecy < 8000, freq_differnece = 5. 
		5. 100 < min_frequency < 12500, freq_difference = 50.
		
	Conclusions:
		Estimated safe configs:
			1. 120 < min_frequecy < 6000
			2. 10 < freq_difference
		Extreme Configs:
			1. 120 < min_frequecy < 6000, freq_diff > 2
			2. 100 < min_frequecy < 12500, freq_diff > 50
		Template_configs:
			1. Max Bass Sounds: min_frequecy = 120, freq_diff = 2
			2. Safe Config: min_frequecy = 120, freq_diff = 50
			2. Max Treble Sounds: min_frequecy = 12500, freq_diff = 50
		
			

			
	
