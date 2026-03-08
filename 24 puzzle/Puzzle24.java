/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
// package com.mycompany.puzzle5;

/**
 *
 * @author rened
 */
import java.util.ArrayList;
import java.util.List;



public class Puzzle24 {

    public static final int N = 5; 
    public static final int SIZE = N * N; 

    public static String[] generarSucesores(String estadoActual) {
        if (estadoActual == null || estadoActual.length() != SIZE) {
            throw new IllegalArgumentException("el estado debe tener exactamente 25 caracteres (5x5).");
        }

        int idx = estadoActual.indexOf(' ');
        if (idx == -1) {
            throw new IllegalArgumentException("el estado debe contener un espacio ' ' como casilla vacía.");
        }

        int r = idx / N;
        int c = idx % N;

        List<String> sucesores = new ArrayList<>(4);

        if (r > 0) sucesores.add(swap(estadoActual, idx, idx - N));     // arriba
        if (r < N - 1) sucesores.add(swap(estadoActual, idx, idx + N)); // abajo
        if (c > 0) sucesores.add(swap(estadoActual, idx, idx - 1));     // izquierda
        if (c < N - 1) sucesores.add(swap(estadoActual, idx, idx + 1)); // derecha

        return sucesores.toArray(new String[0]);
    }

    private static String swap(String s, int i, int j) {
        char[] arr = s.toCharArray();
        char tmp = arr[i];
        arr[i] = arr[j];
        arr[j] = tmp;
        return new String(arr);
    }
}