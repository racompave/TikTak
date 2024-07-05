# Flask demo

import flask
import json
import flask_login
import sirope
from model.User import User
from model.Video import Video
from model.Comentario import Comentario
import werkzeug.security as safe

"""Creación de los objetos de gestion de sesion, Flask como framework y Sirope para almacenamiento"""
def create_app():
    lmanager = flask_login.login_manager.LoginManager()
    fapp = flask.Flask(__name__)
    syrp = sirope.Sirope()

    fapp.config.from_file("config.json", load=json.load)
    lmanager.init_app(fapp)
    return fapp, lmanager, syrp


app, lm, srp = create_app()


"""Devuelve el usuario con el email especificado"""

@lm.user_loader
def user_loader(email):
    return User.find(srp, email)


"""Muestra un error y redirecciona a la pagina de inicio"""

@lm.unauthorized_handler
def unauthorized_handler():
    flask.flash("ERROR: Unauthorized")
    return flask.redirect("/")


"""Accede a la vista de inicio del sitio web"""

@app.route("/")
def get_index():
    return flask.render_template("index.html")


"""Al rellenar el formulario para loguearse obtenemos los campos introducidos
por el usuario y seguidamente comprobamos sobre base de datos si el email
pertenece a un usuario registrado y si la contraseña para ese usuario es correcta. De no ser así,
mostramos los mensajes de error pertinentes redirigiendo sobre la pagina en que ya estamos(pagina de inicio). 
Si los datos son correctos redirigimos hacia la vista principal de usuario logueado"""

@app.route("/login", methods=["POST"])
def login():
    email = flask.request.form["email"]
    password = flask.request.form["password"]
    usr = User.find(srp, email)
    if not usr:
        flask.flash("ERROR: No existe ningún usuario con ese correo")
        return flask.redirect("/")
    elif not usr.chk_password(password):
        flask.flash("ERROR: Contraseña incorrecta")
        return flask.redirect("/")
    else:
        flask_login.login_user(usr)
        return flask.redirect(flask.url_for("start", user=email))


"""Esta ruta de la aplicación presenta la pantalla que se verá nada más loguearse, donde se
cargan los 10 videos más recientemente añadidos, los comentarios de estos videos, y una lista que identifica si
el usuario que está usando la plataforma ha dado like a los videos, con el fin de manipular el correspondiente valor
del botón para dar like. Si el usuario activo no ha dado like a un video concreto, el botón servirá para añadir un like 
y si el usuario ya ha dado like a un video este botón indicará "No me gusta" y servirá  para quitar el like al video
**NOTA: Para listar los videos de la pagina inicial estuve usando srp.load_last(Video, 10) pero me estaba dando
problemas porque saltaba un error 500 despues de eliminar un video, por lo que opte por cambiarla por enumerate,
ordenarlos por fecha y almacenar los 10 primeros en la lista"""

@app.route("/start")
def start():
    usr = User.current_user()
    comentarios_list = []
    videos_list = list(srp.enumerate(Video))
    videos_list.sort(key=lambda video: video.time, reverse=True)
    videos_list = videos_list[:10]
    liked_videos = []
    for video in videos_list:
        if usr.email in video.likedBy:
            liked_videos.append(video.url)
        for comentario in list(Comentario.findByUrl(srp, video.url)):
            comentarios_list.append(comentario)
    sust = {
        "email": usr.email,
        "videos_list": videos_list,
        "liked_videos": liked_videos,
        "comentarios_list": comentarios_list
    }
    return flask.render_template("start.html", **sust)


"""Cerramos la sesión activa en ese momento y redirigimos a la pagina de inicio"""

@app.route("/logout", methods=["POST"])
def logout():
    flask_login.logout_user()
    return flask.redirect("/")


"""Si entra por GET mostramos la vista con el formulario para registrarse.
Si entra por POST cogemos los datos introducidos por el usuario y comprobamos
que el nombre de usuario introducido no está registrado ya. De ser así mostramos
un mensaje de error. Si todo está correcto vamos a la ruta registerOk"""

@app.route("/register", methods=["GET", "POST"])
def register():
    if flask.request.method == "POST":
        email = flask.request.form["email"]
        password = safe.generate_password_hash(flask.request.form["password"])
        usr = User.find(srp, email)
        if not usr:
            usr = User(email, password)
            srp.save(usr)
            return flask.redirect(flask.url_for("registerOk"))
        else:
            flask.flash("ERROR: Ya existe un usuario con ese correo.")
            return flask.redirect(flask.url_for("register"))
    else:
        return flask.render_template("register.html")


"""Esta ruta, simplemente carga una vista en la que la plataforma confirma
que el registro se ha realizado correctamente y avisa al usuario de que regrese
a la página de inicio para loguearse y empezar a utilizar la plataforma"""

@app.route("/registerOk")
def registerOk():
    return flask.render_template("registerOk.html")


"""Si entra por GET mostramos la vista con el formulario para añadir un nuevo video.
Si entra por POST recogemos los datos introducidos por el usuario. Si se detecta que el video
que se quiere añadir ya se encuentra en la plataforma, si ha sido el usuario activo el que había añadido este video 
anteriormente se muestra un mensaje de error instandole a que añada
uno diferente. Si ha sido otro usuario el que ya había añadido este video anteriormente, se muestra una vista con el
video en cuestión y se avisa al usuario de que otro ya había añadido el video. Si todo está correcto se añade el video
y se redirige a la pantalla principal pudiéndose ver el video añadido como primero de la lista de videos."""

@app.route("/addVideo", methods=["GET", "POST"])
def addVideo():
    usr = User.current_user()
    if flask.request.method == "POST":
        url = flask.request.form["url"]
        video = Video.find(srp, url)

        if video:
            if usr.email == video.autor:
                flask.flash("ERROR: Ya has añadido este video! Elige otro")
                return flask.redirect(flask.url_for("addVideo", user=usr.email))
            else:
                videos_list = []
                liked_videos = []
                comentarios_list = []
                videos_list.append(video)
                if usr.email in video.likedBy:
                    liked_videos.append(video.url)
                for comentario in list(Comentario.findByUrl(srp, video.url)):
                    comentarios_list.append(comentario)
                sust = {
                    "email": usr.email,
                    "videos_list": videos_list,
                    "liked_videos": liked_videos,
                    "comentarios_list": comentarios_list
                }
                return flask.render_template("videoCoincidence.html", **sust)
        else:
            autor = usr.email
            description = flask.request.form["description"]
            categoria = flask.request.form["categoria"]
            video = Video(url, autor, description, categoria)
            srp.save(video)
            return flask.redirect(flask.url_for("start", user=usr.email))

    sust = {
        "email": usr.email
    }

    return flask.render_template("addVideo.html", **sust)


"""Esta ruta de la aplicación no carga una vista en sí, si no que manipula la base de datos incrementando en 1 las 
visualizaciones de un video mediante el método addVisualizacion() si el usuario ha hecho click sobre la URL de uno de 
los videos y devuelve una respuesta JSON con el nuevo número de visualizaciones con el fin de manipular este valor 
dinamicamente en el DOM"""

@app.route('/incrementar_visualizacion', methods=['POST'])
def incrementar_visualizacion():
    data = flask.request.json
    url = data.get('url')
    video = Video.find(srp, url)
    if video:
        video.addVisualizacion()
        srp.save(video)
        return flask.jsonify({'success': True, 'newVisualizaciones': video.visualizaciones})
    else:
        return flask.jsonify({'success': False, 'error': 'Video not found'}), 404


"""Esta ruta de la aplicación no carga una vista en sí, si no que manipula la base de datos incrementando en 1 el 
número de likes de un video mediante el método addLike() si el usuario ha hecho click sobre el botón de "Me gusta" en 
uno de los videos y devuelve una respuesta JSON con el nuevo número de likes con el fin de manipular este valor 
dinamicamente en el DOM"""

@app.route('/incrementar_likes', methods=['POST'])
def incrementar_likes():
    data = flask.request.json
    url = data.get('url')
    video = Video.find(srp, url)
    usr = User.current_user()
    if video:
        if usr.email not in video.likedBy:
            video.addLike(usr.email)
            srp.save(video)
            return flask.jsonify({'success': True, 'newLikes': video.nlikes})
    else:
        return flask.jsonify({'success': False, 'error': 'Video not found'}), 404


"""Esta ruta de la aplicación no carga una vista en sí, si no que manipula la base de datos decrementando en 1 el 
número de likes de un video mediante el método removeLike() si el usuario ha hecho click sobre el botón de "No me 
gusta" en uno de los videos y devuelve una respuesta JSON con el nuevo número de likes con el fin de manipular este 
valor dinamicamente en el DOM"""

@app.route('/decrementar_likes', methods=['POST'])
def decrementar_likes():
    data = flask.request.json
    url = data.get('url')
    video = Video.find(srp, url)
    usr = User.current_user()
    if video:
        if usr.email in video.likedBy:
            video.removeLike(usr.email)
            srp.save(video)
            return flask.jsonify({'success': True, 'newLikes': video.nlikes})
    else:
        return flask.jsonify({'success': False, 'error': 'Video not found'}), 404


"""Simplemente carga la vista con la que buscar videos"""

@app.route('/searchVideos', methods=['GET'])
def searchVideos():
    usr = User.current_user()

    sust = {
        "email": usr.email
    }

    return flask.render_template("searchVideos.html", **sust)


"""Carga los videos con las características que hemos especificado en los parámetros de búsqueda.
Si los valores numéricos se dejan en blanco se considerarán como 0, así como si dejamos el autor en blanco o
la fecha sin especificar con su valor predeterminado se ignorará en la búsqueda al igual que los campos
de categoría y orden. Si especificamos un orden, se ordenarán los videos teniendo en cuenta esa clave de orden. Para los
videos que empaten en cuanto a tener el mismo número de visualizaciones, likes o comentarios, se ordenarán por fecha. 
Si no se especifica ningún orden, directamente se ordenan todos por fecha, desde el más reciente al más antiguo."""

@app.route('/searchResults', methods=['POST'])
def searchResults():
    usr = User.current_user()
    autor = flask.request.form["autor"]
    visualizaciones = flask.request.form["visualizaciones"]
    if visualizaciones == "":
        visualizaciones = "0"
    likes = flask.request.form["likes"]
    if likes == "":
        likes = "0"
    comentarios = flask.request.form["comentarios"]
    if comentarios == "":
        comentarios = "0"
    fecha = flask.request.form["fecha"]
    if fecha == "yy/dd/mmmm":
        fecha = ""
    categoria = flask.request.form["categoria"]
    if categoria == "--Sin especificar--":
        categoria = ""
    orden = flask.request.form["orden"]
    videos_list = list(Video.findVideos(srp, autor, visualizaciones, likes, comentarios, fecha, categoria))
    if orden == "--Sin especificar--":
        videos_list.sort(key=lambda video: video.time, reverse=True)
    elif orden == "Visualizaciones":
        videos_list.sort(key=lambda video: (video.visualizaciones, video.time), reverse=True)
    elif orden == "Likes":
        videos_list.sort(key=lambda video: (video.nlikes, video.time), reverse=True)
    else:
        videos_list.sort(key=lambda video: (video.ncomentarios, video.time), reverse=True)
    liked_videos = []
    comentarios_list = []
    for video in videos_list:
        if usr.email in video.likedBy:
            liked_videos.append(video.url)
        for comentario in list(Comentario.findByUrl(srp, video.url)):
            comentarios_list.append(comentario)
    sust = {
        "email": usr.email,
        "liked_videos": liked_videos,
        "videos_list": videos_list,
        "comentarios_list": comentarios_list
    }

    return flask.render_template("searchResults.html", **sust)


"""Carga una vista con los videos que ha añadido el usuario activo a la plataforma, se manda al HTML un flag myVideos 
a True para poder identificar en el HTML que efectivamente estamos en esta vista de manera que se pueda cargar el 
botón de eliminar videos, ya que esta es la unica vista donde podemos acceder a la opción de eliminar nuestros 
videos."""

@app.route("/myVideos", methods=["GET"])
def myVideos():
    usr = User.current_user()
    liked_videos = []
    videos_list = list(Video.findVideosAutor(srp, usr.email))
    videos_list.sort(key=lambda video: video.time, reverse=True)
    comentarios_list = []
    myVideos = True
    for video in videos_list:
        if usr.email in video.likedBy:
            liked_videos.append(video.url)
        for comentario in list(Comentario.findByUrl(srp, video.url)):
            comentarios_list.append(comentario)
    sust = {
        "email": usr.email,
        "liked_videos": liked_videos,
        "videos_list": videos_list,
        "comentarios_list": comentarios_list,
        "myVideos": myVideos
    }
    return flask.render_template("myVideos.html", **sust)


"""Carga una vista con los videos a los que ha dado like el usuario activo en la plataforma, esta vista tiene la 
característica de que al pulsar el botón de "No me gusta" los videos cargados iran desapareciendo dinamicamente de la 
vista sin tener que recargarla"""
@app.route("/likedVideos", methods=["GET"])
def likedVideos():
    usr = User.current_user()
    videos_list = list(Video.findByLike(srp, usr.email))
    liked_videos = []
    comentarios_list = []
    for video in videos_list:
        liked_videos.append(video.url)
        for comentario in list(Comentario.findByUrl(srp, video.url)):
            comentarios_list.append(comentario)
    sust = {
        "email": usr.email,
        "videos_list": videos_list,
        "liked_videos": liked_videos,
        "comentarios_list": comentarios_list
    }
    return flask.render_template("likedVideos.html", **sust)


"""Recogemos en formato JSON el texto introducido por el usuario para el comentario y el url del video a comentar y 
creamos el objeto Comentario con estos datos, guardamos el comentario en base de datos y modificamos 
tambien el video comentado en base de datos ya que al haber modificado su número de 
comentarios debemos actualizar este campo 
con la longitud de número de  comentarios que hay para
la url de ese video. Finalmente devolvemos una respuesta JSON con el comentario en formato diccionario para poder 
acceder a el facilmente con JavaScript y el nuevo numero de comentarios para ese video, con los cuales modificaremos
el DOM de forma dinámica añadiendo el comentario al video"""

@app.route("/comentarVideo", methods=["POST"])
def comentarVideo():
    usr = User.current_user()
    data = flask.request.json
    url = data.get('url')
    texto = data.get('comentario')
    comentario = Comentario(url, usr.email, texto)
    video = Video.find(srp, url)

    if comentario:
        srp.save(comentario)
        num_comentarios = len(list(Comentario.findByUrl(srp, url)))
        video.ncomentarios = num_comentarios
        srp.save(video)
        return flask.jsonify(
            {'success': True, 'message': 'Comentario added successfully', 'comentario': comentario.to_dict(),
             'ncomentarios': num_comentarios})
    else:
        return flask.jsonify({'success': False, 'message': 'No se encontro comentario'}), 404


"""Recogemos la url del video que queremos eliminar y cargamos una vista con este video
y todos sus datos. Esta vista permitirá al usuario poder confirmar si verdaderamente desea
eliminar el video o no. Se manda a la vista un flag eliminarVideo a True para identificar que
estamos en la vista de confirmación de eliminar video para ocultar los botones de "Me gusta" y "Comentar"""

@app.route("/confirmarEliminarVideo", methods=['POST'])
def confirmarEliminarVideo():
    usr = User.current_user()
    url = flask.request.form["url"]
    video = Video.find(srp, url)
    videos_list = []
    liked_videos = []
    videos_list.append(video)
    if usr.email in video.likedBy:
        liked_videos.append(video.url)
    comentarios_list = list(Comentario.findByUrl(srp, url))
    eliminarVideo = True

    sust = {
        "email": usr.email,
        "url": url,
        "liked_videos": likedVideos,
        "videos_list": videos_list,
        "comentarios_list": comentarios_list,
        "eliminarVideo": eliminarVideo
    }

    return flask.render_template("confirmarEliminarVideo.html", **sust)


"""El usuario decide eliminar el video, por lo tanto, eliminamos el video en cuestión de base de datos identificandolo
mediante el OID y además realizamos una eliminación en cascada de todos los comentarios vinculados a ese video"""

@app.route("/eliminarVideo", methods=['POST'])
def eliminarVideo():
    usr = User.current_user()
    url = flask.request.form["url"]
    video = Video.find(srp, url)
    comentarios_list = list(Comentario.findByUrl(srp, url))
    if flask.request.form["confirmacion"] == "si":
        srp.delete(video.__oid__)
        for comentario in comentarios_list:
            srp.delete(comentario.__oid__)

        return flask.redirect(flask.url_for("myVideos", user=usr.email))

    else:
        return flask.redirect(flask.url_for("myVideos", user=usr.email))


"""Se recogen el url del video y el id de comentario mediante JSON y se guardan en dos variables el Video y Comentario
que identifican. Se borra de base de datos el comentario identificándolo mediante el OID"""

@app.route("/eliminarComentario", methods=["POST"])
def eliminarComentario():
    data = flask.request.json
    url = data.get('url')
    id = data.get('id')
    comentario = Comentario.find(srp, id)
    video = Video.find(srp, url)
    if comentario:
        srp.delete(comentario.__oid__)
        num_comentarios = len(list(Comentario.findByUrl(srp, url)))
        video.ncomentarios = num_comentarios
        srp.save(video)
        return flask.jsonify(
            {'success': True, 'message': 'Comentario borrado', 'ncomentarios': num_comentarios})
    else:
        return flask.jsonify({'success': False, 'message': 'No se encontro comentario'}), 404
