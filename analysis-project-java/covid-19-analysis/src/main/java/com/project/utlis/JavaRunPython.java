package com.project.utlis;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class JavaRunPython
{
    public static void run(String json) throws IOException, InterruptedException
    {
        String exe = "python";
        String command = "/home/titanic/soft/pycharm_workspace/analysis-project/analysis-project-java/covid-19-analysis/src/main/resources/python_plot/AreaPlot.py";

        String[] cmdArr = new String[]{exe, command, json};
        Process process = Runtime.getRuntime().exec(cmdArr);
        BufferedReader in = new BufferedReader(new InputStreamReader(process.getInputStream(),"utf-8"));
        String str = in.readLine();
        process.waitFor();
        System.out.println(str);
    }

}
