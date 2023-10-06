# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Bot
from .forms import BotForm

def bot_view(request, id=None):
    if id:
        bot = get_object_or_404(Bot, id=id)
        if request.method == 'POST':
            form = BotForm(request.POST, instance=bot)
            if form.is_valid():
                form.save()
                return redirect('bot_view', id=bot.id)
        else:
            form = BotForm(instance=bot)
    else:
        if request.method == 'POST':
            form = BotForm(request.POST)
            if form.is_valid():
                bot = form.save()
                return redirect('bot_view', id=bot.id)
        else:
            form = BotForm()
    return render(request, 'bot_form.html', {'form': form})
