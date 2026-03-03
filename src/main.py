from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import urllib.parse

load_dotenv()

app = FastAPI()

# Configuración de carpetas
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generar")
async def generar(prompt: str = Form(...)):
    
    safe_prompt = prompt.replace("'", "\\'").replace('"', '\\"').replace("\n", " ")
    encoded_prompt = urllib.parse.quote(prompt)
    
    
    api_key = os.getenv("key_API")
   
    
    img_html = ""
    for i in range(4):
        seed = 2000 + i
        
        url = f"https://gen.pollinations.ai/image/{encoded_prompt}?model=flux&seed={seed}&width=1024&height=1024&key={api_key}"
        
        img_html += (
            f"<div class='bg-gray-800 rounded-2xl overflow-hidden shadow-xl border border-white/5 relative'>"
            f"<img src='{url}' loading='lazy' "
            f"class='w-full cursor-pointer hover:scale-105 transition duration-500' "
            f"onerror=\"this.src='https://placehold.co/1024x1024/ff4444/fff/png?text=Error+al+generar+(ver+F12)'; "
            f"this.nextSibling.style.display='flex';\" "
            f"onclick=\"elegir('{url.replace("'", "\\'")}', '{safe_prompt}')\">"
            f"<div class='absolute inset-0 flex items-center justify-center bg-gray-900/70 hidden text-white text-center p-6'>"
            f"  <div>"
            f"    <svg class='animate-spin h-12 w-12 mx-auto mb-4 text-cyan-400' xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24'>"
            f"      <circle class='opacity-25' cx='12' cy='12' r='10' stroke='currentColor' stroke-width='4'></circle>"
            f"      <path class='opacity-75' fill='currentColor' d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'></path>"
            f"    </svg>"
            f"    <p class='text-lg font-bold'>Generando diseño {i+1}...</p>"
            f"    <p class='text-sm mt-2'>Puede tardar 5-20 segundos. .</p>"
            f"  </div>"
            f"</div>"
            f"</div>"
        )

    
    content = f"""
    <div class="text-center animate-in fade-in duration-700">
        <h2 class="text-3xl font-bold mb-8 text-white">Elige tu diseño favorito</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
            {img_html}
        </div>
        <p class="mt-8 text-slate-400 text-sm">
            
        </p>
    </div>
    
    <div id="form-container"></div>

    <script>
    function elegir(url, p) {{
        const target = document.getElementById('form-container');
        target.innerHTML = `
        <div class='bg-white/10 backdrop-blur-xl p-8 rounded-3xl border border-white/20 max-w-lg mx-auto shadow-2xl mt-12 mb-12 animate-in slide-in-from-bottom duration-500'>
            <h3 class='text-2xl font-bold mb-6 text-center text-white'>Detalles del Pedido</h3>
            <form hx-post='/enviar' hx-target='#resultado' class='space-y-4'>
                <input type='hidden' name='imagen' value='" + url + "'>
                <input type='hidden' name='prompt' value='" + p + "'>
                
                <div>
                    <label class='text-xs text-slate-400 ml-2'>Nombre del Cliente</label>
                    <input type='text' name='nombre' placeholder='Tu nombre completo' required class='w-full p-4 rounded-xl bg-black/40 text-white border border-white/10 focus:border-cyan-500 outline-none'>
                </div>
                
                <div>
                    <label class='text-xs text-slate-400 ml-2'>Número de WhatsApp</label>
                    <input type='tel' name='telefono' placeholder='Ej: +504 9999-9999' required class='w-full p-4 rounded-xl bg-black/40 text-white border border-white/10 focus:border-cyan-500 outline-none'>
                </div>

                <div>
                    <label class='text-xs text-slate-400 ml-2'>Dirección Exacta</label>
                    <textarea name='direccion' placeholder='Barrio, calle, número de casa...' required class='w-full p-4 rounded-xl bg-black/40 text-white border border-white/10 focus:border-cyan-500 outline-none h-24'></textarea>
                </div>

                <div>
                    <label class='text-xs text-slate-400 ml-2'>Cantidad de Totes</label>
                    <input type='number' name='cantidad' value='1' min='1' required class='w-full p-4 rounded-xl bg-black/40 text-white border border-white/10 focus:border-cyan-500 outline-none'>
                </div>

                <button type='submit' class='w-full bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-400 hover:to-emerald-500 text-white font-bold py-4 rounded-2xl transition transform hover:scale-[1.02] active:scale-95 shadow-lg'>
                    Confirmar Pedido por WhatsApp
                </button>
            </form>
        </div>`;
        
        htmx.process(target);
        
        setTimeout(() => {{
            target.scrollIntoView({{behavior: 'smooth', block: 'center'}});
        }}, 100);
    }}
    </script>
    """
    return HTMLResponse(content=content)

@app.post("/enviar")
async def enviar(
    nombre: str = Form(...), 
    telefono: str = Form(...), 
    direccion: str = Form(...), 
    cantidad: int = Form(...),
    imagen: str = Form(...),
    prompt: str = Form(...)
):
    # Aquí puedes procesar el envío de WhatsApp o Email
    return f"""
    <div class='text-center py-20 animate-in zoom-in duration-500'>
        <div class='inline-flex items-center justify-center w-20 h-20 bg-green-500 rounded-full mb-6 shadow-[0_0_20px_rgba(34,197,94,0.5)]'>
            <svg class='w-10 h-10 text-white' fill='none' stroke='currentColor' viewBox='0 0 24 24'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='3' d='M5 13l4 4L19 7'></path></svg>
        </div>
        <h2 class='text-4xl font-bold text-white mb-2'>¡Gracias, {nombre}!</h2>
        <p class='text-green-400 text-xl font-medium'>Pedido de {cantidad} tote(s) recibido correctamente.</p>
        <p class='text-slate-400 mt-4'>Nos pondremos en contacto al {telefono}.</p>
    </div>
    """