package com.covid19.analysis;

import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.SparkSession;

public class AreaPlot
{
    public static String path = "/home/titanic/soft/pycharm_workspace/analysis-project/analysis-project-java/covid-19-analysis/src/main/resources/covid_19_clean_complete.csv";

    public static void main(String[] args)
    {
        SparkSession spark = SparkSession.builder().
                master("spark://titanic:7077").
                appName("AreaPlot").
                getOrCreate();

        Dataset<Row> data = spark
                .read()
                .option("inferSchema", "true")
                .option("header", "true")
                .format("com.databricks.spark.csv")
                .load(path);
        

    }
}
