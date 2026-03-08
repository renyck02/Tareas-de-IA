/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 */

// package com.mycompany.puzzle5;

/**
 *
 * @author rened
 */


import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class Proyecto {


    static final String OBJETIVO = "123456789ABCDEFGHIJKLMNO ";

    public static void main(String[] args) {

     
        int mezcla = 30;          
        long seed = System.nanoTime(); // cambia cada ejecucion

        String inicial = generarEstadoInicialAleatorio(OBJETIVO, mezcla, seed);

        System.out.println("seed usado: " + seed);
        System.out.println("estado inicial:");
        imprimirTablero5x5(inicial);
        System.out.println("====================================");

        // manhatan
        ejecutar(OBJETIVO, inicial, SolverIDA.Heuristica.MANHATTAN);

        // la otra heuristica
        ejecutar(OBJETIVO, inicial, SolverIDA.Heuristica.MISPLACED_TILES);
        
    
    }

    static void ejecutar(String objetivo, String inicial, SolverIDA.Heuristica h) {
        Nodo raiz = new Nodo(inicial);
        SolverIDA solver = new SolverIDA();

        SolverIDA.Resultado res = solver.idaStar(raiz, objetivo, h);

        System.out.println("heuristica: " + h);
        if (res.objetivo == null) {
            System.out.println("no hay solucioomn");
            System.out.println("nodos expandidos" + res.nodosExpandidos);
            System.out.println("nodos generados" + res.nodosGenerados);
            System.out.println("tiempo (ms) " + res.tiempoMs);
            System.out.println("------------------------------------");
            return;
        }

        System.out.println("solucion encontrada");
        System.out.println("movimientos: " + res.movimientos);
        System.out.println("nodos expandidos: " + res.nodosExpandidos);
        System.out.println("nodos generados: " + res.nodosGenerados);
        System.out.println("tiempo (ms): " + res.tiempoMs);

        // imprimir camino
        List<String> camino = SolverIDA.reconstruirCaminoEstados(res.objetivo);
        System.out.println("camino (" + (camino.size() - 1) + " movimientos):");
        for (String e : camino) {
            imprimirTablero5x5(e);
            System.out.println("-----");
        }
        System.out.println("------------------------------------");
    }

    // genera el aleatorio
  
    static String generarEstadoInicialAleatorio(String objetivo, int movimientos, long seed) {
        Random rnd = new Random(seed);
        String estado = objetivo;
        String anterior = null;

        for (int i = 0; i < movimientos; i++) {
            String[] suc = Puzzle24.generarSucesores(estado);

            ArrayList<String> opciones = new ArrayList<>();
            for (String s : suc) {
                if (!s.equals(anterior)) opciones.add(s);
            }

            String siguiente = opciones.get(rnd.nextInt(opciones.size()));
            anterior = estado;
            estado = siguiente;
        }
        return estado;
    }

    static void imprimirTablero5x5(String s) {
        for (int i = 0; i < 25; i += 5) {
            System.out.println(s.substring(i, i + 5));
        }
    }
}