cd C:\rob\SVN\Python\FlightBot
rem activate conda
call C:\Users\Roberto\Anaconda3\condabin\activate.bat
rem launch
call C:\Users\Roberto\Anaconda3\python FlightCrawler_v01.py 1>flight_log.txt 2> flight_err.txt

rem call C:\Users\Roberto\Anaconda3\condabin\deactivate.bat