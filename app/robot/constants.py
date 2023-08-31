URLS = {
    "SAT_LOGIN":            "https://pe.siat.sat.gob.mx/app/PE/emp/accesoEF?parametro=4",
    "SAT_ACTAS":            "https://rfcampe.siat.sat.gob.mx/app/PE/IdcSiat/SACVisorTributario/SACBusquedaVisorTributario.jsf",
    "BASE_URL":             "https://rfc-actas.herokuapp.com",
    # "BASE_URL":             "http://127.0.0.1:5000",
}

ELEMENTS = {
    # *SAT LOGIN*
    "FILE_CER_ID":          "fileCertificate",
    "FILE_KEY_ID":          "filePrivateKey",
    "PASSWORD_ID":          "privateKeyPassword",
    "SUBMIT_LOGIN_ID":      "submit",
    "VALIDATE_LOGIN_ID":    "ErrorTable",
    # *SAT GET COOKIES*
    "SERVICIOS_XPATH":      "//li[@id='arbolMenuForm:menuArbol:1']/span/span",
    "IDENTIFICACION_XPATH": "//li[@id='arbolMenuForm:menuArbol:1_1']/span/span",
    "CONSULTA_XPATH":       "//li[@id='arbolMenuForm:menuArbol:1_1_1']/span/span",
    "VISOR_TRIBU_XPATH":    "//span[@title='Visor Tributario']",
    # *SAT DATOS*
    "ERROR_PANEL_ID":       "error_panel_form",
    "P_FISICA_ID":          "visorForm:radioBtnContribuyente:0",
    "P_MORAL_ID":           "visorForm:radioBtnContribuyente:1",
    "P_MORAL_CSS":          "#visorForm\\:radioBtnContribuyente td:nth-child(4) label",
    "RFC_P_MORAL_ID":       "visorForm:busquedaRFCPersonaMoral",
    "P_MORAL_SEARCH_TAG":   "button",
    "RFC_ID":               "visorForm:busquedaRFCFisica",
    "CURP_ID":              "visorForm:busquedaCurp",
    "NAME_ID":              "visorForm:busquedaNombre",
    "FIRST_LAST_NAME_ID":   "visorForm:busquedaApePaterno",
    "SECOND_LAST_NAME_ID":  "visorForm:busquedaApeMaterno",
    "SEARCH_BTN_ID":        "visorForm:btnBuscar",
    "CLAVE_RFC_CSS":        "#visorForm\\:tablaResultados_data tr a",
    "RES_NAME_CSS":         "#visorForm\\:tablaResultados_data tr :nth-child(1) label",
    "RES_L_NAME_CSS":       "#visorForm\\:tablaResultados_data tr :nth-child(2) label",
    "LOADING_ID":           "j_idt8",
    "ERROR_SUMMARY_CLASS":  "ui-messages-error-summary",
    # *SAT RESUMEN*
    #"GEN_CONSTANCIA_ID":    "visorForm:j_idt233", # *NO FUNCIONA*
    "GEN_CONSTANCIA_CSS":   "#visorForm > table td :nth-child(4)",
    "CANCELAR_ID":          "visorForm:btnCancelar",
    "ACEPTAR_ID":           "visorForm:btnAceptar",
    
}

SCRIPTS = {
    "SEARCH_SCRIPT":        "PrimeFaces.ab({source:'visorForm:btnBuscar',update:'visorForm:tablaResultados visorForm:datosBusquedaPersonaFisica'});",
    "SELECT_USER_SCRIPT":   "PrimeFaces.ab({source:'visorForm:tablaResultados:0:j_idt62',global:false,params:[{name:'rowIdx',value:'0'}]});",
    "GET_CER":              """
                            fetch("BASE_URL/robot/cer").then( ( res ) => {
                                return res.blob() 
                            } ).then( data => {
                                const cer = new File([data], "nombre.cer")
                                const input_cer = document.getElementById("fileCertificate")
                                const dataTransfer = new DataTransfer()
                                const e = new Event("change");
                                dataTransfer.items.add( cer )
                                input_cer.files = dataTransfer.files
                                input_cer.dispatchEvent(e);
                            } )
                            """,
    "GET_KEY":              """
                            fetch("BASE_URL/robot/key").then( ( res ) => {
                                return res.blob() 
                            } ).then( data => {
                                const key = new File([data], "key.key")
                                const input_key = document.getElementById("filePrivateKey")
                                const dataTransfer = new DataTransfer()
                                const e = new Event("change");
                                dataTransfer.items.add( key )
                                input_key.files = dataTransfer.files
                                input_key.dispatchEvent(e);
                            } )
                            """,
    "GENERATE_CONST":       """
                            PrimeFaces.ab(
                                { 
                                    source: 'ID',
                                    oncomplete: 
                                        function (xhr, status, args) { 
                                            //location.href = "https://rfcampe.siat.sat.gob.mx//app/PE/IdcSiat/IdcGeneraConstancia.jsf";
                                            fetch("/app/PE/IdcSiat/IdcGeneraConstancia.jsf").then( ( res ) => {
                                                return res.blob() 
                                            } ).then( data => {
                                                var a = document.createElement("a");
                                                a.href = window.URL.createObjectURL(data);
                                                a.download = "FILE_NAME" + ".pdf";
                                                a.click();
                                                alert("Constancia generada")
                                            } ) 
                                        } 
                                }
                            );
                            """,
    "DOWNLOAD_CONST":       """
                            fetch("/app/PE/IdcSiat/IdcGeneraConstancia.jsf").then( ( res ) => {
                                return res.blob() 
                            } ).then( data => {
                                var a = document.createElement("a");
                                a.href = window.URL.createObjectURL(data);
                                a.download = "FILE_NAME" + ".pdf";
                                a.click();
                            } )
                            """,
    "LOGOUT_SCRIPT":        "closeSession()",
    "SELECT_P_MORAL":       "document.querySelector('#visorForm\\\\:radioBtnContribuyente td:nth-child(3) input').click()"
}
CONST = {
    "NO_SESSION":            "NO_SESSION", #* La sesión ha expirado, hay que volver a iniciar sesión
    "NO_COOKIES":            "NO_COOKIES", #* Las cookies caducaron (por el momento lo mejor es reiniciar la sesión)
    "SESSION_OK":            "SESSION_OK", #* La sesion puede obtener actas
    "UNKNOWN":               "UNKNOWN",    #* Cuando no se puede determinar el estado de la sesión
    "LOGIN_ERROR":           "LOGIN_ERROR",#* Error al iniciar sesión
    "LOGIN_OK":              "LOGIN_OK",   #* Inicio de sesión exitoso
    "COOKIES_OK":            "COOKIES_OK", #* Las cookies se obtuvieron correctamente
    "COOKIES_ERROR":         "COOKIES_ERROR", #* Hubo un error al obtener las cookies
    "USER_NOT_FOUND":        "USER_NOT_FOUND", #* El usuario no se encontró
    "USER_FOUND":            "USER_FOUND", #* El usuario se encontró
    "DOWNLOAD_ERROR":        "DOWNLOAD_ERROR", #* Hubo un error al descargar el acta
    "DOWNLOAD_OK":           "DOWNLOAD_OK", #* El acta se descargó correctamente
}
