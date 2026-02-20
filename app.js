class node {
  constructor(value){
    this.node = value
    this.right = null 
    this.left = null
  }
}

class BinaryTree {
  constructor() {
    this.root = null
  }

  search(value){
    let node = this.root
    while (node != null){
      if(node.node == value){
        return true
      } else if(value > node.node){
        node = node.right
      } else {
        node = node.left
      }
    }
    return false
  }

  vacio(){
    this.root = null
    return true
  }


  insertar(value){
    const newNode = new node(value)

    if (this.root === null) {
      this.root = newNode
      return true
    }

    let current = this.root
    while (true) {
      if (value === current.node) {
  
        return false
      }

      if (value < current.node) {
        if (current.left === null) {
          current.left = newNode
          return true
        }
        current = current.left
      } else {
        if (current.right === null) {
          current.right = newNode
          return true
        }
        current = current.right
      }
    }
  }

  imprimir(){
    if (this.root === null) {
      console.log("(arbol vacio)")
      return
    }
    this.imprimirRec(this.root, 0)
  }

  imprimirRec(nodo, nivel){
    if (nodo === null) return

    this.imprimirRec(nodo.right, nivel + 1)

  
    console.log("   ".repeat(nivel) + nodo.node)

   
    this.imprimirRec(nodo.left, nivel + 1)
  }

  inOrder(){
    const result = []
    this.inOrderRec(this.root, result)
    console.log(result.join(" -> "))
    return result
  }

  inOrderRec(nodo, result){
    if (!nodo) return
    this.inOrderRec(nodo.left, result)
    result.push(nodo.node)
    this.inOrderRec(nodo.right, result)
  }
}


const arbol = new BinaryTree()
arbol.insertar(10)
arbol.insertar(5)
arbol.insertar(15)
arbol.insertar(3)
arbol.insertar(7)

arbol.imprimir()
arbol.inOrder()
console.log(arbol.search(7))  
console.log(arbol.search(99)) 


