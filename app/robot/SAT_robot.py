from time import sleep
from apscheduler.schedulers.background import BackgroundScheduler
import os
from tempfile import TemporaryDirectory

from app.services.selenium_services import SeleniumRobot
from app.robot.constants import URLS, ELEMENTS, SCRIPTS, CONST #, TEST_URLS, FILES
from app.services.firestore_service import  get_all_constancias_pending, update_constancia_status, upload_file, get_certificate, get_key
from app.models import Constancia
from app.sql_models import ConstanciasModel
from app.config import ProductionConfig as Config


temp_directory = TemporaryDirectory()

scheduler = BackgroundScheduler()
scheduler.start()

class SatRobot:
    def __init__(self):
        self.robot = SeleniumRobot( temp_directory.name )
        self.logged = False
        self.running_job = None
        self.app = None
        self.cer = None
        self.key = None
        self.run_interval_get_constancia()

    def replace_robot(self):
        self.robot.quit()
        self.robot = SeleniumRobot( temp_directory.name )

    def hola_mundo(self):
        self.robot.get( "http://google.com" )
        return "Hola desde " + self.robot.get_title()

    def generate_const_script(self, id, file_name):
        return SCRIPTS["GENERATE_CONST"]\
                        .replace("ID", id)\
                        .replace("FILE_NAME", file_name)
    
    def generate_cer_script(self):
        return SCRIPTS["GET_CER"].replace("BASE_URL", URLS["BASE_URL"])
    
    def generate_key_script(self):
        return SCRIPTS["GET_KEY"].replace("BASE_URL", URLS["BASE_URL"])

    def validate_if_logged(self):
        print("Validando si esta logeado...")

        self.robot.get( URLS["SAT_ACTAS"] )
        self.robot.accept_alert()

        url = self.robot.get_current_url()

        if "auth" in url:
            print("No hay sesion activa")
            return CONST["NO_SESSION"]

        if "VisorTributario.jsf" in url:
            print("Sesion activa")
            return CONST["SESSION_OK"]

        if "Error" in url:
            print("Error con las cookies")
            return CONST["NO_COOKIES"]

        print("No se si esta logeado")
        return CONST["UNKNOWN"]
    
    def login(self, password):
        print("Login...")
        try:
            self.robot.get( URLS["SAT_LOGIN"] )
            self.robot.execute_script(
                self.generate_cer_script(),
            )
            self.robot.execute_script(
                self.generate_key_script(),
            )
            self.robot.write_text(
                self.robot.find_element_by_id( 
                    ELEMENTS["PASSWORD_ID"] 
                ),
                password
            )
            self.robot.click( 
                self.robot.find_element_by_id( 
                    ELEMENTS["SUBMIT_LOGIN_ID"] 
                ) 
            )
            error = self.robot.get_element_text(
                self.robot.wait_for_id_element( "divError", 1 )
            )
            if type(error) == str:
                print(error)
                return CONST["LOGIN_ERROR"]
            else:
                print("Login exitoso")
                return CONST["LOGIN_OK"]
        except Exception as e:
            print(e, "Error en login")
            return CONST["LOGIN_ERROR"]

    def get_cookies(self):
        try:
            print("Getting cookies...")
            self.robot.get( URLS["SAT_LOGIN"] )
            sleep(1)
            if "auth" in self.robot.get_current_url():
                print("No hay sesion activa")
                return CONST["COOKIES_ERROR"]
            self.robot.click(
                # self.robot.wait_for_xpath_element(
                self.robot.wait_for_xpath_element_to_be_clickable(
                    ELEMENTS["SERVICIOS_XPATH"]
                )
            )
            self.robot.click(
                # self.robot.wait_for_xpath_element(
                self.robot.wait_for_xpath_element_to_be_clickable(
                    ELEMENTS["IDENTIFICACION_XPATH"]
                )
            )
            self.robot.click(
                # self.robot.wait_for_xpath_element(
                self.robot.wait_for_xpath_element_to_be_clickable(
                    ELEMENTS["CONSULTA_XPATH"]
                )
            )
            self.robot.click(
                # self.robot.wait_for_xpath_element(
                self.robot.wait_for_xpath_element_to_be_clickable(
                    ELEMENTS["VISOR_TRIBU_XPATH"]
                )
            )
            frame_result = self.robot.wait_for_frame_id( "principal" )
            if type(frame_result) == Exception:
                sleep(10)
                frame_result = self.robot.wait_for_frame_id( "principal" )
                if type(frame_result) == Exception:
                    return CONST["COOKIES_ERROR"]
            # sleep(6)                                    #TODO Revisar como quitar este time
            print("Cookies obtenidas")
            return CONST["COOKIES_OK"]
        except Exception as e:
            print(e, "Error en get_cookies")
            return CONST["COOKIES_ERROR"]

    def find_acta(self, rfc="", curp="", tipo="1"):

        print("Buscando acta...")
        
        self.robot.get( URLS["SAT_ACTAS"] ) #Page to fill the data
        self.robot.accept_alert()
        
        # if not rfc and not curp:
        #     if not name or not (first_last_name or second_last_name):
        #         return "Error: No se proporcionaron los datos suficientes para realizar la búsqueda"
        if tipo == "2":
            sleep(1)
            self.robot.click(
                self.robot.wait_for_css_element(
                    ELEMENTS["P_MORAL_CSS"]
                )
            )
            self.robot.write_text(
                self.robot.wait_for_id_element( 
                    ELEMENTS["RFC_P_MORAL_ID"] 
                ),
                rfc
            )
            self.robot.click(
                self.robot.find_elemt_by_tag_name( 
                    ELEMENTS["P_MORAL_SEARCH_TAG"]
                )
            )
        else:
            self.robot.write_text(
                self.robot.wait_for_id_element( 
                    ELEMENTS["RFC_ID"] 
                ),
                rfc
            )
            self.robot.write_text(
                self.robot.wait_for_id_element( 
                    ELEMENTS["CURP_ID"] 
                ),
                curp
            )
            self.robot.click( 
                self.robot.find_element_by_id( 
                    ELEMENTS["SEARCH_BTN_ID"] 
                )
            )
        print("Empezando busqueda...")
        loading = self.robot.wait_for_id_element_to_be_invisble( 
            ELEMENTS["LOADING_ID"]
        )
        print("Busqueda terminada", loading)
        
        search_result = self.robot.find_element_by_css(         #* Wait for the results table
                ELEMENTS["CLAVE_RFC_CSS"]
            )
        
        if type(search_result) == Exception:
            print("Error en busqueda")
            err_elem = self.robot.wait_for_class_element( 
                ELEMENTS["ERROR_SUMMARY_CLASS"],
                2
            )
            error = self.robot.get_element_text(err_elem)
            return (CONST["USER_NOT_FOUND"], error)
        try:
            nombre = self.robot.get_element_text(
                self.robot.find_element_by_css( 
                    ELEMENTS["RES_NAME_CSS"]
                )
            )
            apellido_paterno = self.robot.get_element_text(
                self.robot.find_element_by_css( 
                    ELEMENTS["RES_L_NAME_CSS"]
                )
            )
            self.robot.click(
                search_result
            )
            return (CONST["USER_FOUND"], f"{nombre} {apellido_paterno}")

        except Exception as e:
            print(e, "Error en find_acta")
            return (CONST["UNKNOWN"], e)

    def download_acta(self, file_name):
        try:
            first_acta = self.robot.wait_for_css_element( 
                ELEMENTS["GEN_CONSTANCIA_CSS"]
            )
            session_id = self.robot.get_attribute(
                first_acta,
                "name"
            )
            if type(session_id) == Exception:
                print("Error al obtener el id de sesión")
                return CONST["DOWNLOAD_ERROR"]
            self.robot.execute_script(
                self.generate_const_script(session_id, file_name)
            )
            print("Descargando acta...")
            #sleep(4)                                    #TODO Revisar como quitar este time
                                                        #!    Tiempo de descarga, a veces es más y no se descarga
            self.robot.wait_for_alert()                 #* Cuando se descarga, se muestra un alert
            self.robot.accept_alert()
            print("Acta descargada")
            sleep(2)
            self.robot.click(
                self.robot.wait_for_id_element( 
                    ELEMENTS["CANCELAR_ID"] 
                )
            )
            self.robot.click(
                self.robot.wait_for_id_element( 
                    ELEMENTS["ACEPTAR_ID"] 
                )
            )
            return CONST["DOWNLOAD_OK"]
        except Exception as e:
            print(e, "Error en download_acta")
            return CONST["DOWNLOAD_ERROR"]
    
    def manage_login(self):
        logged = self.validate_if_logged()
        if logged == CONST["SESSION_OK"]:
            return CONST["SESSION_OK"]
        if logged == CONST["NO_SESSION"]:
            self.replace_robot() #TODO Revisar si esto resuelve el problema de la sesión
            return self.login_sat()
        elif logged == CONST["NO_COOKIES"]:
            self.logout()
            self.replace_robot() #TODO Revisar si esto resuelve el problema de la sesión
            return self.login_sat()

    def logout(self):
        print("Logout...")
        self.robot.get( URLS["SAT_LOGIN"] )
        self.robot.accept_alert()
        try:
            self.robot.execute_script( SCRIPTS["LOGOUT_SCRIPT"] )
        except Exception as e:
            print(e, "Logout error o no?") #* Dice que es un error pero no lo es
        self.robot.accept_alert()
        # sleep(1)
        # self.robot.get( URLS["SAT_LOGIN"] )
        # self.robot.accept_alert()
        # self.robot.execute_script( SCRIPTS["LOGOUT_SCRIPT"] )
        # self.robot.accept_alert()
        # self.remove_job()
        # sleep(1)

    def close(self):
        self.robot.close()

    def quit(self):
        self.robot.quit()
        scheduler.remove_all_jobs()
        return self.app

    def get_cer(self):
        return self.cer
    
    def get_key(self):
        return self.key

    def get_constancia(self):
        print("Obteniendo constancia...")

        #* Check login        
        login = self.manage_login()
        if login != CONST["SESSION_OK"]:    #* If login fails exit expecting the next try will work
            return login

        with self.app.app_context():
            pending = ConstanciasModel.query_download_pending()  #* Get all pending constancias
        #TODO Revisar si es conveniente agregar una condicion para no intentar un acta que ya se haya intentado varias veces

        print("Constancias pendientes: ", len(pending))

        for constancia in pending:
            print("Obteniendo constancia...")
            
            #* Check login
            login = self.manage_login()
            if login != CONST["SESSION_OK"]:    #* If login fails exit expecting the next try will work
                return login

            if constancia.rfc or constancia.curp:
                file_name = constancia.rfc if constancia.rfc else constancia.curp
            else:
                file_name = constancia.name + constancia.first_last_name + constancia.second_last_name

            search_result, res = self.find_acta( rfc=constancia.rfc, curp=constancia.curp, tipo=constancia.tipo )
            print(search_result, res)

            if search_result == CONST["USER_NOT_FOUND"]:
                constancia.state = "ERROR: " + (res if len(res) < 40 else res[0:40])
                with self.app.app_context():
                    ConstanciasModel.update_state( constancia.id, constancia.state )
                continue
            elif search_result == CONST["USER_FOUND"]:
                print("Usuario encontrado")
                download_result = self.download_acta( file_name )
                if download_result == CONST["DOWNLOAD_OK"]:
                    print("Descarga exitosa")
                    file_path = os.path.join( temp_directory.name, file_name + ".pdf" )
                    if os.path.exists( file_path ):
                        constancia.state = "DESCARGADO"
                        f_name = upload_file( file_path, file_name, constancia.owner )
                        print( f_name )
                        with self.app.app_context():
                            ConstanciasModel.update_state( constancia.id, constancia.state, f_name, res )
                    else:
                        print("No se encontró el archivo")
        temp_directory.cleanup()

    def login_sat(self):
        self.cer = get_certificate()
        self.key = get_key()
        sleep(2)
        password = Config.SAT_PASSWORD

        login_result = self.login( password )

        self.cer = None
        self.key = None

        if login_result == CONST["LOGIN_ERROR"]:
            return CONST["LOGIN_ERROR"]

        cookies_result = self.get_cookies()

        if cookies_result == CONST["COOKIES_ERROR"]:
            return CONST["COOKIES_ERROR"]

        print("Sesión iniciada")
        return CONST["SESSION_OK"]

    def run_interval_get_constancia(self):
        print("Iniciando intervalo...")
        if(self.running_job):
            self.running_job.remove()
        job_id = scheduler.add_job( self.get_constancia, 'interval', minutes=3, coalesce=True, max_instances=1, id="get_acta_interval" )
        self.running_job = job_id 

    def run_get_constancia(self):
        scheduler.add_job( self.get_constancia, coalesce=True, max_instances=1, id="get_acta" )

    def remove_job(self):
        print("Eliminando job...")
        if(self.running_job):
            self.running_job.remove()
            self.running_job = None

if __name__ == "__main__":
    sat = SatRobot()
    login_result = sat.login( "" )
    
    if login_result:
        raise ValueError( login_result )

    sat.get_cookies()

    sat.find_acta( rfc="", curp="", name="", first_last_name="", 
        second_last_name="", p_fisica=True )
    sat.get_acta()
    