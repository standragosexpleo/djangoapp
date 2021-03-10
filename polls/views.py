from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.shortcuts import render, redirect
from .models import Choice, Question
from .forms import *
from PIL import Image
from polls.face_recognition import get_emotion
import random
import speech_recognition as sr
from django.views.decorators.csrf import csrf_exempt
import pyaudio


def index_view(request):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'
    latest_question_list = Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]
    return render(request, template_name, {'latest_question_list': latest_question_list})


def convert_pixel(r, g, b, a=1):
    color = "#%02X%02X%02X" % (r, g, b)
    opacity = a
    return color, opacity


def upload_and_save_svg_view(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            image = Image.open('polls/images/' + str(request.FILES['photo']))
            mode = image.mode
            pixels = image.load()
            width, height = image.size
            svg_name = str(request.FILES['photo'])[:-4] + ".svg"
            if "RGB" in mode:
                output = "<svg width=\"%d\" height=\"%d\" viewBox=\"0 0 %d %d\" xmlns=\"http://www.w3.org/2000/svg\">" % (
                width, height, width, height)

                for r in range(height):
                    for c in range(width):
                        color, opacity = convert_pixel(*pixels[c, r])
                        output += "<rect x=\"%d\" y=\"%d\" width=\"1\" height=\"1\" fill=\"%s\" fill-opacity=\"%s\"/>" % (
                        c, r, color, opacity)

                output += "</svg>"

                with open('polls/images/' + svg_name, "w") as f:
                    f.write(output)
            return render(request, 'polls/download.html', {'svg_name': svg_name})
    else:
        form = PhotoForm()
    return render(request, 'polls/upload.html', {'form': form})


def upload_and_recognize_emotion(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            emotion = get_emotion('polls/images/' + str(request.FILES['photo']))
            return render(request, 'polls/recognition.html', {'emotion': emotion})
    else:
        form = PhotoForm()
    return render(request, 'polls/upload_recg.html', {'form': form})


@csrf_exempt
def search(request):

    # logic of view will be implemented here
    # if request.method == 'GET':
    # word = request.POST.get("your_word", "")
    # print(word)
    recognizer = sr.Recognizer()
    ''' recording the sound '''
    with sr.Microphone() as source:
        print("Adjusting noise ")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("Recording for 4 seconds")
        recorded_audio = recognizer.listen(source, timeout=4)
        print("Done recording")
    ''' Recorgnizing the Audio '''
    try:
        print("Recognizing the text")
        text = recognizer.recognize_google(
            recorded_audio,
            language="en-EN"
        )
        print("Decoded Text : {}".format(text))
    except Exception as ex:
        print(ex)
    quotes = Quote.objects.filter(quote_text__contains=text.upper())
    if len(quotes) == 0:
        quote = "No quote found for " + str(text) + "."
    else:
        random_number = random.randint(0, len(quotes))
        quote = quotes[random_number].quote_text
    return render(request, "polls/search_bar.html", {'quote': text})


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Update the model, excluding any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))
