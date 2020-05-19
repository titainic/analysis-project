package com.project.utlis;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class JavaRunPython
{
    public static void run(String jsonData,String pythonPath) throws IOException, InterruptedException
    {
        String exe = "python";

        String[] cmdArr = new String[]{exe, pythonPath, jsonData};
        Process process = Runtime.getRuntime().exec(cmdArr);
        BufferedReader in = new BufferedReader(new InputStreamReader(process.getInputStream(),"utf-8"));
        String str = in.readLine();
        process.waitFor();
        System.out.println(str);
    }

}
