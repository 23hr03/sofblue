const apiBaseUrl = "http://localhost:5000";  // Definir la URL base de la API
const { createApp } = Vue;

createApp({
  data() {
    return {
      formType: 'index', // 'login' o 'registro'
      email: '',
      password: '',
      username: '',
      nuevaContraseña: '',
      error: false,
      cargando: false,
      requestMonitor: null, // Inicializamos 'requestMonitor'
    };
  },
  methods: {
    showForm(formType) {
      this.formType = formType; // Cambia el formulario
    },
    async validarLogin() {
      if (!this.email || !this.password) {
        alert("Por favor, complete todos los campos.");
        return;
      }
    
      this.cargando = true;
      try {
        const response = await fetch(`${apiBaseUrl}/ingresar`, {
          method: 'POST',
          body: JSON.stringify({ email: this.email, password: this.password }),  // Asegúrate de enviar 'password'
          headers: { 'Content-Type': 'application/json' },
        });
    
        const data = await response.json();
        this.cargando = false;
        if (response.ok) {
          alert("Login exitoso.");
          this.resetForm(); // Limpiar formulario
          // Usar la URL de redirección del backend en lugar de una fija
          if (data.redirect) {
            window.location.href = data.redirect; // Redirige a http://localhost:5000/Home
          } else {
            window.location.href = `${apiBaseUrl}/Home`; // Fallback por si no hay redirect
          }
        } else {
          this.requestMonitor = data;
          alert(data.message || "Credenciales inválidas.");
        }
      } catch (error) {
        console.error(error);
        this.cargando = false;
        this.requestMonitor = errorData; // Asignamos la respuesta de error a 'requestMonitor'
        alert("Error al iniciar sesión.");
      }
    },
    

    async logout() {
      try {
        const response = await fetch(`${apiBaseUrl}/logout`, {
          method: 'GET',
          credentials: 'same-origin',
        });
        if (response.ok) {
          localStorage.removeItem('usuario'); // Limpia el usuario del localStorage
          window.location.href = '/index'; // Redirige a la página de login
        } else {
          alert("Error al cerrar sesión.");
        }
      } catch (error) {
        console.error(error);
        alert("Error al cerrar sesión.");
      }
    },

    async validarRegistro() {
      if (!this.username || !this.email || !this.password) {
        alert("Todos los campos son obligatorios.");
        return;
      }
    
      this.cargando = true;
      try {
        const response = await fetch(`${apiBaseUrl}/registro`, {
          method: 'POST',
          body: JSON.stringify({ 
            usuario: this.username, 
            email: this.email, 
            contraseña: this.password }),
          headers: { 'Content-Type': 'application/json' },
        });
    
        const data = await response.json();
        this.cargando = false;
    
        if (response.ok) {
          alert("Registro exitoso.");
          this.resetForm(); // Limpiar formulario
          this.showForm('index');
        } else {
          this.requestMonitor = data;
          alert(data.message || "Error al registrar usuario.");
        }
      } catch (error) {
        console.error(error);
        this.cargando = false;
        alert("Error al registrar usuario.");
      }
    },
    async buscarUsuario() {
      if (!this.username || !this.email) {
        this.error = "Usuario y correo son requeridos.";
        return;
      }

      this.loading = true;
      try {
        const response = await fetch(`${this.apiBaseUrl}/buscar_usuario/${this.username}/${this.email}`, {
          method: 'GET',
          mode: 'cors',
        });

        this.loading = false;

        if (response.redirected) {
          // Extraer el ID del usuario desde la URL redirigida
          const redirectUrl = new URL(response.url);
          this.usuarioId = redirectUrl.pathname.split('/').pop();
          this.formType = 'cambiar'; // Cambiar al formulario de contraseña
        } else {
          const data = await response.json();
          this.error = data.message;
        }
      } catch (error) {
        this.loading = false;
        this.error = "Error al buscar usuario: " + error.message;
      }
    },
    async cambiarContraseña() {
      if (!this.nuevaContraseña) {
        this.error = "Nueva contraseña requerida.";
        return;
      }

      this.loading = true;
      try {
        const response = await fetch(`${this.apiBaseUrl}/cambiar_contraseña/${this.usuarioId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ nueva_contraseña: this.nuevaContraseña }),
          mode: 'cors',
        });

        const data = await response.json();
        this.loading = false;

        if (response.ok) {
          alert("Contraseña actualizada con éxito");
          this.resetForm();
          this.formType = 'buscar';
        } else {
          this.error = data.message;
        }
      } catch (error) {
        this.loading = false;
        this.error = "Error al cambiar contraseña: " + error.message;
      }
    },
    
    
//==================== otra forma de hacer el cambio de contraseña ===================================
    // async actualizarContraseña() {
    //   if (!this.username || !this.email || !this.password) {
    //     alert("Por favor, complete todos los campos.");
    //     return;
    //   }

    //   this.cargando = true;
    //   this.error = '';
    //   try {
    //     const response = await fetch(`${apiBaseUrl}/usuario/${this.username}/${this.email}`, {
    //       method: 'PUT',
    //       headers: { 'Content-Type': 'application/json' },
    //       body: JSON.stringify({ password: this.password }),
    //     });

    //     const data = await response.json();
    //     this.cargando = false;

    //     if (response.ok) {
    //       alert("Contraseña actualizada exitosamente.");
    //       this.resetForm(); // Limpiar formulario
    //     } else {
    //       alert(data.message || "Error al actualizar la contraseña.");
    //     }
    //   } catch (err) {
    //     console.error(err);
    //     this.cargando = false;
    //     alert("Hubo un error al hacer la solicitud.");
    //   }
    // },
// =============================================================================================================
    resetForm() {
      this.username = '';
      this.email = '';
      this.password = '';
    },
  },
  template: `
    <div>
      <div v-if="formType === 'index'">
        <h2>Inicio de sesión</h2>
        <form @submit.prevent="validarLogin">
          <label for="login-email">Correo Electrónico:</label>
          <input type="email" v-model="email" id="login-email" required>

          <label for="login-password">Contraseña:</label>
          <input type="password" v-model="password" id="login-password" required>

          <input type="submit" value="Iniciar Sesión">
          <button type="button" @click="showForm('registro')">Regístrate</button>
          <button type="button" @click="showForm('cambio_C')">Olvidé mi contraseña</button>
        </form>
      </div>

      <div v-if="formType === 'registro'">
        <h2>Regístrate</h2>
        <form @submit.prevent="validarRegistro">
          <label for="username">Usuario:</label>
          <input type="text" v-model="username" id="username" required><br>

          <label for="registro-email">Correo Electrónico:</label>
          <input type="email" v-model="email" id="registro-email" required><br>

          <label for="registro-password">Contraseña:</label>
          <input type="password" v-model="password" id="registro-password" required><br>

          <input type="submit" value="Registrarse">
          <button type="button" @click="showForm('login')">Iniciar sesión</button>
        </form>
      </div>

     <div v-if="formType === 'buscar'">
      <h2>Buscar Usuario</h2>
      <form @submit.prevent="buscarUsuario">
        <label>Usuario:</label>
        <input v-model="username" type="text" required>
        <label>Correo:</label>
        <input v-model="email" type="email" required>
        <button type="submit" :disabled="loading">Buscar</button>
      </form>
    </div>

    <div v-if="formType === 'cambiar'">
      <h2>Cambiar Contraseña</h2>
      <form @submit.prevent="cambiarContraseña">
        <label>Nueva Contraseña:</label>
        <input v-model="nuevaContraseña" type="password" required>
      <button type="submit" :disabled="loading">Actualizar</button>
    </form>
    </div>
    

      <div v-if="cargando">Cargando...</div>
      <div v-if="error">Hubo un error en la operación.</div>
    </div>
  `,

}).mount('#app');
