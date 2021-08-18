# Vaccines Trade Network: An implementation with ARIMA, Holt-Winters and Neural Networks

![Python](https://img.shields.io/badge/-Python-000?&logo=Python) ![Jupyter Notebook](https://img.shields.io/badge/Jupyter-Notebook-orange?&logo=Jupyter)

Implementation of ARIMA, Holt-Winters Exponential Smoothing and Neural Network models for the analysis of the global network of human vaccines for the period 2010-2020. On top of the main analysis, we are creating an interactive dashboard to present our results, via the usage of the [Dash](https://dash.plotly.com/) library.


### Details

Scope of this project is to replicate the global trade network of human vaccines around the globe for a variety of years (current data span from 2010 to 2020). Through plotting and statistical analysis, we want to identify informative patterns on how different countries change their import/export activity throughout the years. We will use a variety of visualization tools and plots to get a better understanding of the main importers/exporters of vaccines, identify pairs of countries that tend to trade with each other regularly, and more. Finally, by using observations from the aforementioned timeframe we will attempt to predict future values of the trade activity between any two pair of countries. Specifically, we will use the the trade value of vaccines from 2010 to 2019 and create two forecasting models which will allow us to predict the monthly trade values for 2020 between _United Kingdom_ and _USA_.

##### Data Source
The monthly data for vaccine expornts/imports have been collected from com https://comtrade.un.org/.

### Data Retrieval API

To retrieve the data from the source website, we have implemented a script that automatically makes calls to the comtrade.un.org website and collects data for each country available. The script takes as input a list of years (or just a single year) that we are interested into and we want to retrieve data for.

Guide/Steps:

  1. Use the _data\_retrieval.py_ from the command line, and when prompted, provide a list of the years of interest for which you want to retrieve monthly data for.
        ``` 
        python data_retrieval.py -years 2019 2020
        ```
  This process will create a separate CSV file per country.

  2. Run _data\_cleaning.py_ to merge the data into a single CSV, _per year_. Note that if a CSV file from step 1. was empty - indicating that there was no data for a specific country - then this country will be missing completely from the final merged CSV file. The cleaning script is currently taking as input _one_ year per execution time.
        ``` 
        python data_cleaning.py 2019 
        ```

</br></br></br>
##### Useful links that helped my research while developing this project:

  1. https://towardsdatascience.com/python-interactive-network-visualization-using-networkx-plotly-and-dash-e44749161ed7
  2. https://medium.com/plotly/introducing-dash-5ecf7191b503
  3. https://towardsdatascience.com/how-to-build-a-complex-reporting-dashboard-using-dash-and-plotl-4f4257c18a7f
  4. https://towardsdatascience.com/a-gentle-invitation-to-interactive-visualization-with-dash-a200427ccce9
  5. https://dash.plotly.com/layout
  6. https://towardsdatascience.com/time-series-forecasting-with-deep-stacked-unidirectional-and-bidirectional-lstms-de7c099bd918
  7. https://nwfsc-timeseries.github.io/atsa-labs/sec-tslab-correlation-within-and-among-time-series.html
  8. https://www.machinelearningplus.com/time-series/arima-model-time-series-forecasting-python/
  9. https://www.curiousily.com/posts/time-series-forecasting-with-lstms-using-tensorflow-2-and-keras-in-python/
  10. https://machinelearningmastery.com/time-series-forecasting-methods-in-python-cheat-sheet/
  
