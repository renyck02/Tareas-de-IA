/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
// package com.mycompany.puzzle5;

/**
 *
 * @author rened
 */

/**
 * Solucionador IDA* para 24-puzzle (o cualquier sliding puzzle)
 * usando tu clase Nodo (estado String, padre, nivel, generarSucesores()).
 */



import java.util.*;

public class SolverIDA {

    public enum Heuristica {
        MANHATTAN,
        MISPLACED_TILES
    }

    // metricas
    private long nodosExpandidos;
    private long nodosGenerados;
    private long inicioNs;

    // objetivo y mapa ficha->pos objetivo
    private String objetivoStr;
    private Map<Character, Integer> goalIndex;

    public static class Resultado {
        public final Nodo objetivo;
        public final long nodosExpandidos;
        public final long nodosGenerados;
        public final long tiempoMs;
        public final int movimientos;

        public Resultado(Nodo objetivo, long exp, long gen, long tMs, int movimientos) {
            this.objetivo = objetivo;
            this.nodosExpandidos = exp;
            this.nodosGenerados = gen;
            this.tiempoMs = tMs;
            this.movimientos = movimientos;
        }
    }

    private static class SearchResult {
        Nodo found;
        int minNext;
        SearchResult(Nodo found, int minNext) {
            this.found = found;
            this.minNext = minNext;
        }
    }

    public Resultado idaStar(Nodo raiz, String estadoObjetivo, Heuristica hType) {
        if (raiz == null) return new Resultado(null, 0, 0, 0, -1);

        if (estadoObjetivo == null || estadoObjetivo.length() != raiz.estado.length()) {
            throw new IllegalArgumentException("el objetivo debe tener el mismo largo que el estado (25).");
        }

        this.objetivoStr = estadoObjetivo;
        this.goalIndex = construirGoalIndex(estadoObjetivo);

        this.nodosExpandidos = 0;
        this.nodosGenerados = 0;
        this.inicioNs = System.nanoTime();

        int threshold = heuristica(raiz.estado, hType);

        HashSet<String> pathSet = new HashSet<>();
        pathSet.add(raiz.estado);

        // asegurar la raiz 
        raiz.padre = null;
        raiz.nivel = 0;

        while (true) {
            SearchResult res = dfsBounded(raiz, 0, threshold, hType, pathSet);

            if (res.found != null) {
                long tMs = (System.nanoTime() - inicioNs) / 1_000_000;
                int moves = res.found.nivel;
                return new Resultado(res.found, nodosExpandidos, nodosGenerados, tMs, moves);
            }

            if (res.minNext == Integer.MAX_VALUE) {
                long tMs = (System.nanoTime() - inicioNs) / 1_000_000;
                return new Resultado(null, nodosExpandidos, nodosGenerados, tMs, -1);
            }

            threshold = res.minNext;
        }
    }

    private SearchResult dfsBounded(Nodo actual, int g, int threshold,
                                   Heuristica hType, HashSet<String> pathSet) {

        int h = heuristica(actual.estado, hType);
        int f = g + h;

        if (f > threshold) {
            return new SearchResult(null, f);
        }

        if (actual.estado.equals(objetivoStr)) {
            return new SearchResult(actual, threshold);
        }

        // expandimos este nodo
        nodosExpandidos++;

        int minNext = Integer.MAX_VALUE;

        List<Nodo> sucesores = actual.generarSucesores();
        nodosGenerados += sucesores.size();

        for (Nodo s : sucesores) {

            if (pathSet.contains(s.estado)) continue; // evita ciclos en la ruta actual

            
            s.padre = actual;
            s.nivel = actual.nivel + 1;

            pathSet.add(s.estado);
            SearchResult res = dfsBounded(s, g + 1, threshold, hType, pathSet);
            pathSet.remove(s.estado);

            if (res.found != null) return res;
            if (res.minNext < minNext) minNext = res.minNext;
        }

        return new SearchResult(null, minNext);
    }

    // heuristicas

    private int heuristica(String estado, Heuristica tipo) {
        return switch (tipo) {
            case MANHATTAN -> manhattan(estado);
            case MISPLACED_TILES -> misplacedTiles(estado);
        };
    }

    // distancia manhattan
    private int manhattan(String estado) {
        final int N = Puzzle24.N;
        int dist = 0;

        for (int i = 0; i < estado.length(); i++) {
            char tile = estado.charAt(i);
            if (tile == ' ') continue;

            int goalPos = goalIndex.get(tile);
            int r1 = i / N, c1 = i % N;
            int r2 = goalPos / N, c2 = goalPos % N;
            dist += Math.abs(r1 - r2) + Math.abs(c1 - c2);
        }
        return dist;
    }

    // cuantas fichas no estan en su lugar
    private int misplacedTiles(String estado) {
        int h = 0;
        for (int i = 0; i < estado.length(); i++) {
            char c = estado.charAt(i);
            if (c == ' ') continue;
            if (c != objetivoStr.charAt(i)) h++;
        }
        return h;
    }

    private Map<Character, Integer> construirGoalIndex(String objetivo) {
        Map<Character, Integer> map = new HashMap<>();
        for (int i = 0; i < objetivo.length(); i++) {
            map.put(objetivo.charAt(i), i);
        }
        return map;
    }

    // camino
    public static List<String> reconstruirCaminoEstados(Nodo objetivo) {
        LinkedList<String> camino = new LinkedList<>();
        Nodo n = objetivo;
        while (n != null) {
            camino.addFirst(n.estado);
            n = n.padre;
        }
        return camino;
    }
}