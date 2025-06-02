from flask import Flask, render_template, request, redirect, session, jsonify
from database import create_tables, add_admin_user, create_connection
import bcrypt, sqlite3, os

app = Flask(__name__)
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = 'static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
create_tables()
add_admin_user('admin', 'admin123')

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/Nosotros")
def about():
    return render_template("about.html")

@app.route("/Servicios")
def services():
    return render_template("services.html")

@app.route("/Marcas")
def brands():
    return render_template("brands.html")

@app.route("/buscar", methods=["GET"])
def search():
    query = request.args.get("query", "").lower()
    if "productos" in query:
        return redirect("/productos")
    return redirect("/")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("logged_in"):
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT username, password FROM usuarios WHERE username = ?', (username,))
            user = cursor.fetchone()
            conn.close()

            if user:
                stored_password = user[1]
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')):
                    session["logged_in"] = True
                    return redirect("/admin") 
                else:
                    return render_template("admin.html", error="Contraseña incorrecta.")
            else:
                return render_template("admin.html", error="Usuario no encontrado.")
        
        return render_template("admin.html", error=None)

    message = ""
    if request.method == "POST":
        codigo = float (request.form.get("codigo"))
        nombre = request.form.get("nombre")
        categoria = request.form.get("categoria")
        precio = float(request.form.get("precio"))
        descripcion = request.form.get("descripcion")

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO productos (codigo, nombre, categoria, precio, descripcion)
            VALUES (?, ?, ?, ?, ?)
            ''', (codigo, nombre, categoria, precio, descripcion))
            conn.commit()
            message = "Producto agregado exitosamente."
        except sqlite3.Error as e:
            message = f"Error al agregar producto: {e}"
        finally:
            conn.close()

    return render_template("admin.html", message=message)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/admin") 

@app.route("/productos", methods=["GET"])
def productos():
    categoria = request.args.get("categoria", None)
    nombre = request.args.get("nombre", None)

    conn = create_connection()
    cursor = conn.cursor()

    if nombre:
        cursor.execute("SELECT codigo, nombre, categoria, precio, descripcion FROM productos WHERE nombre LIKE ?", (f"%{nombre}%",))
        productos = cursor.fetchall()
    elif categoria:
        cursor.execute("SELECT codigo, nombre, categoria, precio, descripcion FROM productos WHERE categoria = ?", (categoria,))
        productos = cursor.fetchall()
    else:
        cursor.execute("SELECT codigo, nombre, categoria, precio, descripcion FROM productos")
        productos = cursor.fetchall()
    conn.close()
    return render_template("products.html", productos=productos, categoria=categoria)

@app.route("/admin/add", methods=["POST"])
def add_product():
    if session.get("logged_in"):
        codigo = request.form.get("codigo")
        nombre = request.form.get("nombre")
        categoria = request.form.get("categoria")
        precio = float(request.form.get("precio"))
        descripcion = request.form.get("descripcion")
        imagen = request.files.get("imagen")
        imagen_filename = None

        if imagen:
            imagen_filename = os.path.join(app.config['UPLOAD_FOLDER'], imagen.filename)
            imagen.save(imagen_filename)

        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO productos (codigo, nombre, categoria, precio, descripcion, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                (codigo, nombre, categoria, precio, descripcion, imagen_filename)
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error al agregar producto: {e}")
        finally:
            conn.close()

    return redirect("/admin")

@app.route("/admin/show", methods=["GET"])
def show_all_products():
    if session.get("logged_in"): 
        conn = create_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, codigo, nombre, categoria, precio, descripcion, imagen FROM productos")
            productos = cursor.fetchall()
            productos_json = [
                {"id": row[0],
                "codigo": row[1],
                "nombre": row[2],
                "categoria": row[3],
                "precio": row[4],
                "descripcion": row[5],
                "imagen": row[6],
                }
                for row in productos
            ]
        except sqlite3.Error as e:
            print(f"Error al recuperar productos: {e}")
            productos_json = []
        finally:
            conn.close()

        return jsonify(productos_json) 
    else:
        return jsonify({"error": "No autorizado"}), 401

@app.route("/admin/product/<int:id>", methods=["GET"])
def get_product(id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, codigo, nombre, categoria, precio, descripcion, imagen FROM productos WHERE id = ?', (id,))
    producto = cursor.fetchone()
    conn.close()

    if producto:
        return jsonify({
            "id": producto[0],
            "codigo": producto[1],
            "nombre": producto[2],
            "categoria": producto[3],
            "precio": producto[4],
            "descripcion": producto[5],
            "imagen": producto[6]
        })
    else:
        return jsonify({"error": "Producto no encontrado"}), 404

@app.route("/admin/update/<int:id>", methods=["PUT"])
def update_product(id):
    if session.get("logged_in"):
        conn = create_connection()
        cursor = conn.cursor()

        # Extrae datos del formulario
        codigo = request.form.get("codigo")
        nombre = request.form.get("nombre")
        categoria = request.form.get("categoria")
        precio = float(request.form.get("precio"))
        descripcion = request.form.get("descripcion")
        nueva_imagen = request.files.get("image")
        imagen_path = None

        # Actualiza imagen si se sube una nueva
        if nueva_imagen:
            imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], nueva_imagen.filename)
            nueva_imagen.save(imagen_path)

        try:
            if imagen_path:  # Si hay nueva imagen, actualiza también el campo imagen
                cursor.execute(
                    """UPDATE productos 
                    SET codigo = ?, nombre = ?, categoria = ?, precio = ?, descripcion = ?, imagen = ? 
                    WHERE id = ?""",
                    (codigo, nombre, categoria, precio, descripcion, imagen_path, id)
                )
            else:  # Si no, actualiza solo los demás campos
                cursor.execute(
                    """UPDATE productos 
                    SET codigo = ?, nombre = ?, categoria = ?, precio = ?, descripcion = ? 
                    WHERE id = ?""",
                    (codigo, nombre, categoria, precio, descripcion, id)
                )
            conn.commit()
            return jsonify({"success": True})
        except sqlite3.Error as e:
            print(f"Error al actualizar producto: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
        finally:
            conn.close()
    return jsonify({"success": False, "error": "No autorizado"}), 401

@app.route('/admin/delete/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # Ejecutar la eliminación
        cursor.execute("DELETE FROM productos WHERE id = ?", (product_id,))
        conn.commit()  # Confirmar los cambios
        conn.close()
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    
@app.route("/admin/search", methods=['GET'])
def search_products():
    nombre = request.args.get("nombre", '').strip()
    categoria = request.args.get("categoria", '').strip()
    query = "SELECT * FROM productos WHERE 1=1"
    params = []

    if nombre:
        query += " AND nombre LIKE ?"
        params.append(f"%{nombre}%")
    if categoria:
        query += " AND categoria LIKE ?"
        params.append(f"%{categoria}%")

    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        productos = cursor.fetchall()

    return render_template("admin.html", productos=productos)

@app.route("/buscar_sugerencias")
def buscar_sugerencias():
    query = request.args.get('query', '').strip().lower()
    if not query:
        return jsonify([])

    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT categoria FROM productos WHERE categoria LIKE ?", ('%' + query + '%',))
    categorias = cursor.fetchall()

    sugerencias = []
    
    if categorias:
        for categoria in categorias:
            sugerencias.append({'nombre': categoria[0], 'categoria': 'Categoría'})
    else:
        cursor.execute("SELECT DISTINCT nombre FROM productos WHERE nombre LIKE ?", ('%' + query + '%',))
        productos = cursor.fetchall()
        
        for producto in productos:
            sugerencias.append({'nombre': producto[0], 'categoria': 'Producto'})
    conn.close()
    return jsonify(sugerencias)

@app.route("/buscar_productos", methods=["GET"])
def buscar_productos():
    query = request.args.get('query', '')
    if query:
        conn = sqlite3.connect("distribuidora_chavez.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM productos
            WHERE nombre LIKE ? OR categoria LIKE ?
        """, ('%' + query + '%', '%' + query + '%'))
        productos = cursor.fetchall()
        conn.close()
        return jsonify(productos)
    return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)