package com.covid19.analysis;

import com.google.gson.Gson;
import com.project.utlis.JavaRunPython;
import org.apache.spark.api.java.function.MapFunction;
import org.apache.spark.sql.AnalysisException;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import org.apache.spark.sql.RowFactory;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.catalyst.encoders.RowEncoder;
import org.apache.spark.sql.functions;
import org.apache.spark.sql.types.DataTypes;

import java.io.IOException;
import java.util.List;

import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.concat_ws;
import static org.apache.spark.sql.functions.split;
import static org.apache.spark.sql.functions.sum;

public class AreaPlot
{
    public static String path = "/home/titanic/soft/pycharm_workspace/analysis-project/analysis-project-java/covid-19-analysis/src/main/resources/data/covid_19_clean_complete.csv";

    public static void main(String[] args) throws AnalysisException, IOException
    {
        SparkSession spark = SparkSession.builder().
                master("spark://titanic:7077").
                appName("AreaPlot").
                getOrCreate();
        spark.sparkContext().addJar("/home/titanic/soft/pycharm_workspace/analysis-project/analysis-project-java/covid-19-analysis/target/covid-19-analysis-1.0-SNAPSHOT.jar");

        Dataset<Row> data = spark
                .read()
                .option("inferSchema", "true")
                .option("header", "true")
                .format("com.databricks.spark.csv")
                .load(path).select(col("Date"), col("Confirmed"), col("Deaths"), col("Recovered"));

        Dataset<Row> activeDS = data.withColumn("Active", functions.lit(0));

        Dataset<Row> active2DS = activeDS.map(new MapFunction<Row, Row>()
        {
            public Row call(Row row) throws Exception
            {
                int confirmed = row.getInt(1);
                int deaths = row.getInt(2);
                int recovered = row.getInt(3);
                int active = confirmed - deaths - recovered;
                return RowFactory.create(
                        row.getString(0),
                        row.getInt(1),
                        row.getInt(2),
                        row.getInt(3),
                        active);
            }
        }, RowEncoder.apply(activeDS.schema()));

        Dataset<Row> active3DS = active2DS.na().fill(0);
//        Dataset<Row> active4DS = active3DS.groupBy("Date").agg(sum(col("Recovered")).as("Recovered"), sum(col("Deaths")).as("Deaths"), sum(col("Active")).as("Active"));

        //2/2/20 日期 按照'/'拆分成多列,修改年20为2020
        Dataset<Row> active5DS = active3DS.withColumn("Date", split(col("Date"), "/")).select(
                col("Date").getItem(0).as("mm"),
                col("Date").getItem(1).as("dd"),
                col("Date").getItem(2).as("yy"),
                col("Recovered"),
                col("Deaths"),
                col("Active"));


        Dataset<Row> active6DS = active5DS.map(new MapFunction<Row, Row>()
        {
            public Row call(Row row) throws Exception
            {
                String yy = row.getString(2);

                return RowFactory.create(
                        row.getString(0),
                        row.getString(1),
                        yy + "20",
                        row.getInt(3),
                        row.getInt(4),
                        row.getInt(5));
            }
        }, RowEncoder.apply(active5DS.schema()));

        //合并拆分的列,并转换数据类型为日期类型
        Dataset<Row> active7DS = active6DS.select(concat_ws("-", col("yy"), col("mm"), col("dd")).as("Date").cast(DataTypes.DateType),
                col("Recovered"),
                col("Deaths"),
                col("Active")).
                sort(col("Date"));

        Dataset<Row> active8DS = active7DS.groupBy("Date").agg(sum(col("Recovered")).as("Recovered"), sum(col("Deaths")).as("Deaths"), sum(col("Active")).as("Active"));
        active8DS.createTempView("active8DS");

        //防坑指南  ->  'Recovered' , `Recovered` , Date,不一样
        Dataset<Row> active9DS = active8DS.sqlContext().sql("SELECT Date , STACK(3,'Recovered',`Recovered`,'Deaths',`Deaths`,'Active',`Active`) AS (`Case`,`Count`) FROM active8DS");

        List<String> jsonList = active9DS.toJSON().collectAsList();

        Gson g = new Gson();
        String json = g.toJson(jsonList);
        System.out.println(json);

        spark.stop();
        json = json.replace("\\", "");
        json = json.replace("\"{", "{");
        json = json.replace("}\"", "}");
        json = "'"+json+"'";
        System.out.println(json);
        try
        {
            JavaRunPython.run(json);
        } catch (InterruptedException e)
        {
            e.printStackTrace();
        }
    }
}
