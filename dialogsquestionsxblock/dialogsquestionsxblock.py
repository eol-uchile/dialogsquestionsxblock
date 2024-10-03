from ipaddress import v6_int_to_packed
import pkg_resources

from django.template import Context, Template

from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, Boolean, Dict, Float
from xblock.fragment import Fragment
from xblockutils.studio_editable import StudioEditableXBlockMixin
import datetime
import pytz

utc=pytz.UTC

# Make '_' a no-op so we can scrape strings
_ = lambda text: text

import logging
logger = logging.getLogger(__name__)


class DialogsQuestionsXBlock(StudioEditableXBlockMixin, XBlock):

    display_name = String(
        display_name=_("Display Name"),
        help=_("Display name for this module"),
        default="Eol Dialogs with Questions XBlock",
        scope=Scope.settings,
    )

    icon_class = String(
        default="other",
        scope=Scope.settings,
    )

    image_url = String(
        display_name=_("URL del personaje"),
        help=_("Indica la URL a la imagen del personaje en el dialogo"),
        default="https://static.sumaysigue.uchile.cl/cmmeduformacion/produccion/assets/img/diag_aldo.png",
        scope=Scope.settings,
    )

    image_size = Integer(
        display_name=_("tamaño del personaje"),
        help=_("(Solo en REDFID)"),
        default=112,
        scope=Scope.settings,
    )

    flip_image = Boolean(
        display_name=_('Invertir personaje'),
        help=_('Invertir imagen del personaje'),
        default=False,
        scope=Scope.settings,
    )

    background_color = String(
        display_name=_("Color de fondo"),
        help=_("Color del contenedor del dialogo"),
        default="#F8E37B",
        scope=Scope.settings,
    )

    border_color = String(
        display_name=_("Color del borde"),
        help=_("Color del borde del contenedor del dialogo"),
        default="#F8E37B",
        scope=Scope.settings,
    )

    text_color = String(
        display_name=_("Color del texto"),
        help=_("Color del texto del dialogo"),
        default="#000000",
        scope=Scope.settings,
    )

    side = String(
        display_name = _("Posicion"),
        help = _("Indica la posicion del dialogo"),
        default = "Izquierda",
        values = ["Izquierda", "Derecha"],
        scope = Scope.settings
    )

    character_name = String(
        display_name=_("Nombre del personaje (RedFid)"),
        help=_("Solo disponible en RedFid"),
        default="Firulais",
        scope=Scope.settings,
    )

    text = String(
        display_name="Contenido del dialogo", 
        multiline_editor='html', 
        resettable_editor=False,
        default="<p>Contenido del dialogo.</p>", 
        scope=Scope.settings,
        help=_("Indica el contenido del dialogo, si se quieren incluir entradas de texto," 
            "usar el formato &lt;span class='inputdialogo'&gt;respuesta correcta_otra respuesta correcta&lt;/span&gt; y si se quieren "
            "incluir dropdowns &lt;span class='dropdowndialogo'&gt;opcion incorrecta,(opcioncorrecta),opcion incorrecta&lt;/span&gt; <br/> Si necesitas utilizar la coma como símbolo puede usar estos caracteres '⸴ ⹁ ､ ⸒'"
        )
    )

    theme = String(
        display_name = _("Estilo"),
        help = _("Cambiar estilo de la pregunta"),
        default = "SumaySigue",
        values = ["SumaySigue", "Media","RedFid"],
        scope = Scope.settings
    )

    globo = String(
        display_name = _("globo"),
        help = _("Cambiar tipo de globo de dialogo (solo SumaySigue)"),
        default = "dialogo",
        values = ["dialogo", "pensamiento"],
        scope = Scope.settings
    )


    answers = Dict(
        help=_(
            'Respuestas de las preguntas'
        ),
        default={},
        scope=Scope.settings,
    )

    student_answers = Dict(
        help=_(
            'Respuestas del estudiante a las preguntas'
        ),
        default={},
        scope=Scope.user_state,
    )

    max_attempts = Integer(
        display_name=_('Nro de Intentos'),
        help=_(
            'Nro de veces que el estudiante puede intentar responder'
        ),
        default=2,
        values={'min': 0},
        scope=Scope.settings,
    )

    weight = Integer(
        display_name='Weight',
        help='Entero que representa el peso del problema',
        default=1,
        values={'min': 0},
        scope=Scope.settings,
    )

    attempts = Integer(
        default=0,
        scope=Scope.user_state,
    )

    show_answer = String(
        display_name = "Mostrar Respuestas",
        help = "Si aparece o no el boton mostrar respuestas",
        default = "Finalizado",
        values = ["Mostrar", "Finalizado", "Ocultar"],
        scope = Scope.settings
    )

    score = Float(
        default=0.0,
        scope=Scope.user_state,
    )

    has_score = True

    icon_class = "problem"

    editable_fields = ('display_name', 'image_url', 'image_size', 'flip_image', 'background_color', 'border_color', 'text_color', 'side', 'character_name', 'text', 'theme', 'globo', 'max_attempts', 'weight', 'show_answer', 'answers')

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        context_html = self.get_context()
        template = self.render_template('static/html/dialogsq.html', context_html)
        frag = Fragment(template)
        frag.add_css(self.resource_string("static/css/dialogsq.css"))
        frag.add_javascript(self.resource_string("static/js/src/utils.js"))
        frag.add_javascript(self.resource_string("static/js/src/dialogsq.js"))
        settings = {
            'location'  : str(self.location).split('@')[-1],
            'image_path': self.runtime.local_resource_url(self, 'public/images/')
        }
        frag.initialize_js('DialogsQuestionsXBlock', json_args=settings)
        return frag
        
    def studio_view(self, context):
        """
        Render a form for editing this XBlock
        """
        context = {'fields': []}
        # Build a list of all the fields that can be edited:
        for field_name in self.editable_fields:
            field = self.fields[field_name]
            assert field.scope in (Scope.content, Scope.settings), (
                "Only Scope.content or Scope.settings fields can be used with "
                "StudioEditableXBlockMixin. Other scopes are for user-specific data and are "
                "not generally created/configured by content authors in Studio."
            )
            field_info = self._make_field_info(field_name, field)
            if field_info is not None:
                context["fields"].append(field_info)
                if field_name == 'text': 
                    field_info["value"] = field_info["value"].replace("<span></span>","")
        template = self.render_template('static/html/studio_edit.html', context)
        fragment = Fragment(template)
        fragment.add_javascript(self.resource_string("static/js/src/utils.js"))
        fragment.add_javascript(self.resource_string("static/js/src/studio_edit.js"))
        fragment.initialize_js('StudioEditableXBlockMixin')
        return fragment

    def get_context(self):
        return {
            'xblock': self,
            'indicator_class': self.get_indicator_class(),
            'image_path' : self.runtime.local_resource_url(self, 'public/images/'),
            'show_correctness' : self.get_show_correctness(),
            'location': str(self.location).split('@')[-1],
            'is_past_due': self.get_is_past_due
        }

    def render_template(self, template_path, context):
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        return template.render(Context(context))
    
    def get_show_correctness(self):
        if hasattr(self, 'show_correctness'):
            if self.show_correctness == 'past_due':
                if self.is_past_due():
                    return "always"
                else:
                    return "never"
            else:
                return self.show_correctness
        else:
            return "always"
    
    def get_is_past_due(self):
        if hasattr(self, 'show_correctness'):
            return self.is_past_due()
        else:
            return False

    def is_past_due(self):
        """
        Determine if component is past-due
        """
        # These values are pulled from platform.
        # They are defaulted to None for tests.
        due = getattr(self, 'due', None)
        graceperiod = getattr(self, 'graceperiod', None)
        # Calculate the current DateTime so we can compare the due date to it.
        # datetime.utcnow() returns timezone naive date object.
        now = datetime.datetime.utcnow()
        if due is not None:
            # Remove timezone information from platform provided due date.
            # Dates are stored as UTC timezone aware objects on platform.
            due = due.replace(tzinfo=None)
            if graceperiod is not None:
                # Compare the datetime objects (both have to be timezone naive)
                due = due + graceperiod
            return now > due
        return False


    @XBlock.json_handler
    def savestudentanswers(self, data, suffix=''):  # pylint: disable=unused-argument
        #Reviso si no estoy haciendo trampa y contestando mas veces en paralelo
        errores = False
        if self.max_attempts == None or ((self.attempts + 1) <= self.max_attempts) or self.max_attempts <= 0:
            self.student_answers = data['student_answers']#Respuestas de estudiantes
            #check correctness
            buenas = 0.0
            malas = 0.0
            total = len(self.answers)

            for k,v in list(self.student_answers.items()):
                #Revisa multiples opciones e respuestas
                anstocheck = self.answers[k]
                anstocheck = anstocheck.replace("<span></span>","")

                if anstocheck.find("[_[i]_]") != -1: #Verificar si es input
                    optionsinput = str(anstocheck).replace("[_[i]_]","")
                    optionsinputs = optionsinput.split("_")#Separa las posibles soluciones
                    for option in optionsinputs:
                        if option.strip() == v.strip():
                            buenas += 1
                            break

                elif anstocheck.find("[_[s]_]") != -1: #Verifica si es select
                    optionselect = str(anstocheck).replace("[_[s]_]","")
                    if optionselect.strip() == v.strip():
                        buenas += 1

            malas = (total-buenas)

            #update score and classes
            self.score = float(buenas/(malas+buenas))
            ptje = self.weight*self.score
            try:
                self.runtime.publish(
                    self,
                    'grade',
                    {
                        'value': ptje,
                        'max_value': self.weight
                    }
                )
                self.attempts += 1
            except IntegrityError:
                pass
        else:
            errores = True
        #return to show score
        return {
                'max_attempts': self.max_attempts,
                'attempts': self.attempts, 
                'score':self.score, 
                'indicator_class': self.get_indicator_class(), 
                'show_correctness' : self.get_show_correctness(),
                'show_answer': self.show_answer,
                'errores': errores
            }

    @XBlock.json_handler
    def getanswers(self, data, suffix=''):
        if ( (self.max_attempts is None or self.attempts >= self.max_attempts) and self.show_answer == 'Finalizado') or self.show_answer == 'Mostrar':
            return {'answers': self.answers}
        return {}

    def get_indicator_class(self):
        indicator_class = 'unanswered'
        if self.attempts:
            if self.score >= 1:
                indicator_class = 'correct'
            else:
                indicator_class = 'incorrect'
        return indicator_class

    def max_score(self):
        """
        Returns the configured number of possible points for this component.
        Arguments:
            None
        Returns:
            float: The number of possible points for this component
        """
        return self.weight

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("DialogsQuestionsXBlock",
             """<dialogsquestionsxblock/>
             """),
            ("Multiple DialogsQuestionsXBlock",
             """<vertical_demo>
                <dialogsquestionsxblock
                theme='Media'
                image_url = 'https://static.sumaysigue.uchile.cl/SySMedia/produccion/EPI/T01/A01/img/juanr.png'
                text = '&lt;p&gt;Contenido del dialogo.&lt;p\&gt;Indica elato &lt;span class="inputdialogo"&gt;respuesta correcta&lt;span\&gt; y '
                />
                <dialogsquestionsxblock
                theme='Media'
                image_url = 'https://static.sumaysigue.uchile.cl/SySMedia/produccion/EPI/T01/A01/img/juanr.png'
                side = 'Derecha'
                />
                <dialogsquestionsxblock/>
                </vertical_demo>
             """),
        ]
