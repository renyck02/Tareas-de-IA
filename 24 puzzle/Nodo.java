/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
// package com.mycompany.puzzle5;

import java.util.ArrayList;
import java.util.List;

/**
 *
 * @author rened
 */


public class Nodo {
    public String estado;
    public Nodo padre;
    public int nivel;   

    public Nodo(String estado) {
        this.estado = estado;
        this.padre = null;
        this.nivel = 0;
    }

    public Nodo(String estado, Nodo padre) {
        this.estado = estado;
        this.padre = padre;
        this.nivel = (padre == null) ? 0 : padre.nivel + 1;
    }

    public List<Nodo> generarSucesores() {
        String[] estadoHijos = Puzzle24.generarSucesores(estado);
        List<Nodo> sucesores = new ArrayList<>(estadoHijos.length);

        for (String e : estadoHijos) {
            
            sucesores.add(new Nodo(e, this));
        }
        return sucesores;
    }
}