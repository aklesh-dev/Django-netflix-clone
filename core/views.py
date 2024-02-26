from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Movie, MovieList
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import re

# Create your views here.
@login_required(login_url='login')
def index(request):
    movies = Movie.objects.all() #  Get all the objects in the database for this model
    featured_movie = movies[len(movies)-1] # The last object is the most recent one (featured)
    
    context = {
        'movies': movies, #  Add the list of movies to the context so it can be accessed in the template
        'featured_movie': featured_movie,
    }
    return render(request, 'index.html', context)

@login_required(login_url='login')
def movie(request, pk): 
    movie_uuid = pk
    movie_details = Movie.objects.get(uu_id=movie_uuid) # Get a single object based on its id (pk)
    context = {
        'movie_details': movie_details
    }
    return render(request, 'movie.html', context)

@login_required(login_url="login")
def genra(request, pk):
    movie_genra = pk
    movies = Movie.objects.filter(genre=movie_genra) # Filter the queryset by genre
    context={'movies':movies, 'movie_genra': movie_genra}   
    return render(request, 'genre.html', context)

@login_required(login_url="login")
def search(request):
    if request.method == 'POST': 
        search_term = request.POST['search_term']
        movies = Movie.objects.filter(title__icontains=search_term) # Filter out any result that matches title with the search term

        context = {
            'movies': movies,
            'search_term': search_term 
        }    
        return render(request, 'search.html', context)
    else:
        return redirect('/')

@login_required(login_url="login")
def my_list(request):
    # filter out movie list of current login user  and make it available in the template
    movie_list = MovieList.objects.filter(owner_user=request.user) 
    user_movie_list = []

    for movie in movie_list:
        user_movie_list.append(movie.movie) #  only keep the actual movie object not the uuid 

    context = {
        'movies':user_movie_list
    }
    return render(request, 'my_list.html', context)

@login_required(login_url="login")
def  add_to_list(request):
    if  request.method == "POST":
        movie_url_id = request.POST.get('movie_id') #  get data from form submission
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' #  Regular expression pattern for UUID
        match = re.search(uuid_pattern, movie_url_id)  
        movie_id = match.group() if match else None 

        # Retrieve the movie object from the database using the id from the form submission     
        movie = get_object_or_404(Movie, uu_id=movie_id) 
        # Get or create a user's personal  movie list - will only exist if they have logged in
        movie_list, created = MovieList.objects.get_or_create(owner_user=request.user, movie=movie) 
        # If the movie was successfully added to the list then display a success message and 
        if created:
            response_data = {
                'status': 'success',
                'message':'Added ✔',
            }
        else:
            response_data = { 'status':'info','message':'Already added!'}
        return JsonResponse(response_data)
        
    else:
        return JsonResponse({ 'status':'error','message':'Invalid request'}, status=400) 

# login function
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        # Check if user is register
        if user is not None:
            auth.login(request, user)
            # messages.info(request, f"You are now logged in as {user.username}")
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('login')
    else:
        return render(request, 'login.html')

# signup function
def signup(request):    
    if request.method == 'POST':  # If the form has been submitted...
        # Get the data from a form field        
        email = request.POST['email'] # The name attribute of the <input> element 
        username = request.POST['username'] # Get the username
        password = request.POST['password'] 
        password2 = request.POST['password2']
        #  Check that the two passwords entered match
        if password == password2:
            # The two passwords match. Create the user and log in the user.
            # Checking for existing users by email address 
            if  User.objects.filter(email=email).exists():
                messages.info(request, "Email already registered")
                return redirect('signup') #, {'message':"Email already exists."})
            # Checking for existing users by username
            elif User.objects.filter(username=username).exists():
                messages.error(request,'Username is taken')
                return redirect('signup')
            else:
                # Create a new user object with the given information
                user = User.objects.create_user(username=username, password=password, email=email)
                user.save()
                # Authenticate the user
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                # Add message to show successful registration
                messages.success(request,"Registration Successful! You are now logged in." )
                # And then redirect to the home page.
                return redirect('/')
        else:
            messages.info(request, "Passwords do not match")
            # Return to the registration page
            return render(request, 'signup.html')
    else:
        return render(request, 'signup.html')

# logout function
@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')
