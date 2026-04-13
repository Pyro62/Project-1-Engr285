#A program implementing and measuring a Wa-Tor Simulation (outputs to a "temp" folder)

from matplotlib.pyplot import * #Library needed to plot results
from numpy import * #Library needed for some numerical functions
from random import * #Library needed to generate random numbers for movement
import sys, glob, shutil, os #Libraries needed to read/write files/folders and other system operations
from pathlib import Path #Library to determine the file paths to images
import imageio.v2 as io #Library for converting a collection of image files to a gif
import shutil

#Main parameters of the simulation
breed_time = int(sys.argv[1]) #Number of steps before a fish is capable of duplicating #int
energy_gain = int(sys.argv[2]) #Additional steps granted to a shark after eating a fish #int
breed_energy = int(sys.argv[3]) #Number of stored steps before a shark is capable of duplicating #int

#Other simulation parameters
dims = [int(sys.argv[4]),int(sys.argv[5])] #Size of the simulation window
initial_fish = int(sys.argv[6])
initial_sharks = int(sys.argv[7])
steps = int(sys.argv[8]) #Time duration of the simulation
basicSetup = True #A random initial distribution (or not) # if anything here then it'll be true
if str(sys.argv[9]).lower() == "true":
    basicSetup = True
else:
    basicSetup = False
print(basicSetup)
# to fix, basicsetup is false?
attempt = int(sys.argv[10])
#Create a list of the row indexes of the game array
ilist = []
for i in range(dims[0]):
    ilist.append(i)
#Create a list of the column indexes of the game array
jlist = []
for j in range(dims[1]):
    jlist.append(j)
    
#Function to generate a list of adjacent location indices
def generate_adjacent_indices(row_index, column_index):
    return [[row_index, (column_index+1)%dims[1]], [row_index, (column_index-1)%dims[1]], [(row_index+1)%dims[0], column_index], [(row_index-1)%dims[0], column_index]]

#Function to determine available empty spaces to move into
def remove_occupied(locations): #Input a list of lists of locations and values (should be four adjacent locations)
    open_locations = [] #Create an empty list of locations
    for k in range(4):
        if locations[k][1] == 0: #If the value shows the space is empty...
            open_locations.append(locations[k][0]) #...add the corresponding location to the list of locations
    return open_locations
  
#Function to determine if there are adjacent fish that a shark can feed on
def find_fish_occupied(locations):
    fish_locations = [] #Create an empty list of locations
    for k in range(4): #Input a list of lists of locations and values (should be four adjacent locations)
        if locations[k][1] > 0: #If the value shows the space has a fish there...
            fish_locations.append(locations[k][0]) #...add the corresponding location to the list of locations
    return fish_locations

#Function to determine the common elements in two lists of lists (with no repeats)
def nest_intersection(list1, list2):
    return list(map(list, set(map(tuple, list1)) & set(map(tuple, list2))))
  
#Function to combine all elements in two lists of lists (with no repeats)
def nest_union(list1, list2):
    return list(map(list, set(map(tuple, list1)) | set(map(tuple, list2))))

#Main function of the simulation, updates the game array including all movements, hunts, breedings, and deaths
def step_fish(i,j,old_array,new_array, old_locations,new_locations):
    old_locations = remove_occupied(old_locations)
    new_locations = remove_occupied(new_locations)
    available_locations = nest_intersection(old_locations, new_locations) #Determines which adjacent spaces are free in both arrays
    if len(available_locations) != 0: #Check if there are any options
        chosen_location = available_locations[randint(0, len(available_locations)-1)] #Randomly choose one of the options
        if breed_time < old_array[i][j]: #Check if the fish is elligible to breed
            new_array[chosen_location[0]][chosen_location[1]] = 1 #Place a new fish in that location
            new_array[i][j] = 1 #Reset the fish that just bred
        else: #Otherwise the fish only moves
            new_array[chosen_location[0]][chosen_location[1]] = old_array[i][j] + 1 #The fish moves to the new game array with an increment to its breeding timer
    else: #If there are no options, the fish does not breed or move
        new_array[i][j] = old_array[i][j] #The fish moves to the new game array without resetting 
    old_array[i][j] = 0 #Removes the fish from the previous game array (so that it doesn't move/breed twice)

def step_shark(i, j, old_array, new_array, direction_array, old_locations, new_locations):
    current_dir = direction_array[i][j]
    energy = old_array[i][j]  # negative integer
    hunger_threshold = -breed_energy // 2  # hungrier than half max energy

    # --- Determine sensing radius based on hunger ---
    if energy > hunger_threshold:  # very hungry (energy closer to 0)
        radius = 2
    else:
        radius = 1  # well-fed, only immediate neighbors

    # --- Hunt: find fish within range ---
    save_old_locations = old_locations
    save_new_locations = new_locations
    old_locations = find_fish_occupied(old_locations)
    new_locations = find_fish_occupied(new_locations)
    immediate_fish = nest_union(old_locations, new_locations)

    if radius == 2 and len(immediate_fish) == 0:
        extended_fish = find_fish_in_range(i, j, old_array, radius=2)
        # Only keep fish reachable in one step (adjacent) but bias toward
        # the direction of the nearest detected fish
        if len(extended_fish) > 0:
            target = extended_fish[0]  # closest fish
            di = target[0] - i
            dj = target[1] - j
            # Clamp to one step in the dominant direction
            step_di = 1 if di > 0 else (-1 if di < 0 else 0)
            step_dj = 1 if dj > 0 else (-1 if dj < 0 else 0)
            candidate = [(i+step_di)%dims[0], (j+step_dj)%dims[1]]
            # Only move there if it's actually empty
            if new_array[candidate[0]][candidate[1]] == 0 and old_array[candidate[0]][candidate[1]] == 0:
                chosen_location = candidate
                new_energy = energy + 1  # costs energy to move, no meal
                new_array[chosen_location[0]][chosen_location[1]] = new_energy
                direction_array[chosen_location[0]][chosen_location[1]] = delta_to_dir(step_di, step_dj)
                old_array[i][j] = 0
                direction_array[i][j] = 0
                return

    # eat fish if close enough
    if len(immediate_fish) != 0:
        # bias fish in current direction
        if current_dir != 0:
            dr, dc = dir_to_delta(current_dir)
            preferred = [(i+dr)%dims[0], (j+dc)%dims[1]]
            if preferred in immediate_fish:
                chosen_location = preferred
            else:
                chosen_location = immediate_fish[randint(0, len(immediate_fish)-1)]
        else:
            chosen_location = immediate_fish[randint(0, len(immediate_fish)-1)]

        new_energy = energy - energy_gain
        di = (chosen_location[0]-i) % dims[0]
        dj = (chosen_location[1]-j) % dims[1]
        if di > dims[0]//2: di -= dims[0]
        if dj > dims[1]//2: dj -= dims[1]
        new_dir = delta_to_dir(di, dj)

        if -breed_energy > new_energy:
            new_array[chosen_location[0]][chosen_location[1]] = round(new_energy / 2)
            new_array[i][j] = new_energy - round(new_energy / 2)
            direction_array[chosen_location[0]][chosen_location[1]] = new_dir
            direction_array[i][j] = current_dir
        else:
            new_array[chosen_location[0]][chosen_location[1]] = new_energy
            direction_array[chosen_location[0]][chosen_location[1]] = new_dir

        if old_array[chosen_location[0]][chosen_location[1]] > 0:
            old_array[chosen_location[0]][chosen_location[1]] = 0

    else:
        #No fish then just move with directional persistence 
        old_locations = remove_occupied(save_old_locations)
        new_locations = remove_occupied(save_new_locations)
        available_locations = nest_intersection(old_locations, new_locations)

        if len(available_locations) != 0:
            # bias toward current direction
            chosen_location = None
            if current_dir != 0:
                dr, dc = dir_to_delta(current_dir)
                preferred = [(i+dr)%dims[0], (j+dc)%dims[1]]
                if preferred in available_locations and random() < 0.65:  # 65% chance to continue direction
                    chosen_location = preferred
            if chosen_location is None:
                chosen_location = available_locations[randint(0, len(available_locations)-1)]

            di = (chosen_location[0]-i) % dims[0]
            dj = (chosen_location[1]-j) % dims[1]
            if di > dims[0]//2: di -= dims[0]
            if dj > dims[1]//2: dj -= dims[1]
            new_dir = delta_to_dir(di, dj)

            if -breed_energy > energy:
                new_array[chosen_location[0]][chosen_location[1]] = round(energy / 2)
                new_array[i][j] = energy - round(energy / 2)
                direction_array[chosen_location[0]][chosen_location[1]] = new_dir
                direction_array[i][j] = current_dir
            else:
                new_array[chosen_location[0]][chosen_location[1]] = energy + 1
                direction_array[chosen_location[0]][chosen_location[1]] = new_dir
        else:
            new_array[i][j] = energy + 1  # stuck, lose energy

    old_array[i][j] = 0
    if new_array[i][j] == 0:  # only zero direction if shark actually left
        direction_array[i][j] = 0

def step_game(old_array,direction_array):
    global ilist, jlist
    new_array = zeros((dims[0], dims[1]), dtype=int) #Creates the next game array
    shuffle(ilist) #Randomize the order of the row indices each time (helps keep the processes uniformly random)
    for i in ilist: #Cycle over all row indices in the previous game array
        shuffle(jlist) #Randomize the order of the column indices each time (helps keep the processes uniformly random)
        for j in jlist: #Cycle over all column indices in the previous game array
            if old_array[i][j] != 0: #Check if the space is not empty
                old_locations = [] #Create an empty list for location/value pairs in the old array
                new_locations = [] #Create an empty list for location/value pairs in the new array
                for indices in generate_adjacent_indices(i, j): #For every adjacent location...
                    old_locations.append([indices, old_array[indices[0]][indices[1]]]) #...append a pair including the old array value at that location
                    new_locations.append([indices, new_array[indices[0]][indices[1]]]) #...append a pair including the new array value at that location
                if 0 < old_array[i][j]: #Check if a fish occupies the space
                    step_fish(i,j,old_array,new_array, old_locations,new_locations)
                else: #If an occupied space is not a fish, then it must be a shark
                   step_shark(i,j,old_array,new_array, direction_array, old_locations,new_locations)

    return new_array #Outputs the updated game array

#Function that counts the total number of fish and sharks in the game array
def countsNf(game_array):
    fish_count = 0 #Initialize a fish counter
    shark_count = 0 #Initialize a shark counter
    for i in range(dims[0]): #Cycle over all row...
        for j in range(dims[1]): #...and column indices
            if game_array[i][j] > 0: #If there's a fish there...
                fish_count += 1 #...increment the fish counter
            if game_array[i][j] < 0: #If there's a shark there...
                shark_count += 1 #...increment the shark counter
    return [shark_count, fish_count]
  
#Function to convert the game array into a format for visual display
def create_img_array(game_array):
    img_array = zeros((dims[0], dims[1]), dtype=int)
    for i in range(dims[0]):
        for j in range(dims[1]):
            if game_array[i][j] > 0:
                img_array[i][j] = 1
            if game_array[i][j] < 0:
                img_array[i][j] = -1
    return img_array

game_array = zeros((dims[0],dims[1]), dtype=int) #Initialize the game array
direction_array = zeros((dims[0], dims[1]), dtype=int)
# Encoding: 0=none, 1=up, 2=down, 3=left, 4=right, direction arr for shark pathfinding

def dir_to_delta(d):
    return {1: (-1,0), 2: (1,0), 3: (0,-1), 4: (0,1)}.get(d, (0,0))
#converts direction to row/col deltas
def delta_to_dir(di, dj):
    return {(-1,0):1, (1,0):2, (0,-1):3, (0,1):4}.get((di,dj), 0)

def find_fish_in_range(i, j, old_array, radius=2):
    found = [] # finds fish in radius 2, returns sorted by distance
    for di in range(-radius, radius+1):
        for dj in range(-radius, radius+1):
            if abs(di)+abs(dj) == 0 or abs(di)+abs(dj) > radius:
                continue
            ni, nj = (i+di)%dims[0], (j+dj)%dims[1]
            if old_array[ni][nj] > 0:
                found.append(([ni, nj], abs(di)+abs(dj)))
    found.sort(key=lambda x: x[1])  # closest first
    return [f[0] for f in found]

if basicSetup == True: #The basic set-up with random placement of new fish and sharks
    for k in range(initial_fish): #Randomly populate the game array with new initial fish
        i = randint(0, dims[0]-1)
        j = randint(0, dims[1]-1)
        while game_array[i][j] != 0: #Keep picking different indices until the chosen location is open
            i = randint(0, dims[0]-1)
            j = randint(0, dims[1]-1)
        game_array[i][j] = randint(1, breed_time) #Give the fish a random initial time
    for k in range(initial_sharks): #Randomly populate the game array with new initial sharks
        i = randint(0, dims[0]-1)
        j = randint(0, dims[1]-1)
        while game_array[i][j] != 0: #Keep picking different indices until the chosen location is open
            i = randint(0, dims[0]-1)
            j = randint(0, dims[1]-1)
        game_array[i][j] = randint(-breed_energy, -1) #Give the shark a random initial energy
else: #A less random set-up, where the sharks and fish start grouped together
    for i in range(dims[0]): #Cycle over all entries in the game array
        for j in range(dims[1]):
            if (i-dims[0]/2)**2 + (j-dims[1]/2)**2 < initial_sharks/pi: #Populate a central disk of sharks with random energy
                game_array[i][j] = randint(-breed_energy, -1) #Give the shark a random initial energy
            elif (i-dims[0]/2)**2 + (j-dims[1]/2)**2 < (initial_sharks + initial_fish)/pi: #Populate a ring of fish surrounding the sharks with random time
                game_array[i][j] = randint(1, breed_time) #Give the fish a random initial time

img_array = create_img_array(game_array)
arrayfig = figure(frameon=False)
ax = arrayfig.subplots()
ax.set_axis_off()
img = ax.imshow(img_array, cmap='bwr')
arrayfig.tight_layout()
savefig('tmp0001.png')

fishes = [initial_fish] #Initialize the list to store fish data
sharks = [initial_sharks] #Initialize the list to store the shark data
print("Playing game...")
prcnt = 0
k = 1 #Initialize a counter for the number of steps
actual_steps = steps #Initialize a separate variable to record how many steps the simulation actually runs
while k <= steps:
    game_array = step_game(game_array, direction_array) #Update the game array
    currcount = countsNf(game_array) #Counts the number of fish and sharks
    fishes.append(currcount[1]) #Store the number data
    sharks.append(currcount[0])
    img_array = create_img_array(game_array) #Create a version of the game array that's easier to plot
    img.set_data(img_array) #Draw the plot of the new game array
    savefig('tmp%04d.png' % (k+1)) #Save the new plot to the temporary folder
    if floor(k*100/steps) > prcnt: #Output the progress of the simulation
        ppstr = str(prcnt) + '%'
        sys.stdout.write('%s\r' % ppstr)
        sys.stdout.flush()
        prcnt += 1
    if 0 < currcount[0] + currcount[1] < dims[0] * dims[1]: #Check if the species have not gone extinct and the array isn't full
        k += 1
    else:
        print('Early termination!')
        actual_steps = k #Save the actual number of steps taken
        k = steps + 1 #Push the value of k large enough to terminate the while loop
    
sys.stdout.write('%s\r' % '100%') #Output that the game updates have completed
sys.stdout.flush()

print('Reading image files...')

#Save a string for the file name which includes all the parameters used in the run
filename = 'SnFanimation_'+str(dims[1])+'x'+str(dims[0])+'_('+str(breed_time)+','+str(energy_gain)+','+str(breed_energy)+')_('+str(initial_sharks)+','+str(initial_fish)+')_'+str(actual_steps)+'.gif' #File name for the output gif file, includes relevant simulation parameters
mypath = Path(__file__).parent.absolute() #File path to the temporary image folder
imgnames = glob.glob('tmp*.png') #Generate a list of all image names in the temporary image folder
imgPaths = []

for imgname in imgnames: #Convert the list of image names to a list of file paths to the images
    imgPaths.append(str(mypath/imgname))

imgPaths.sort() #Sort the images into chronological order
totaldata = []

for imgpath in imgPaths: #Read in all the image data
    currdata = io.imread(imgpath)
    totaldata.append(currdata)

directoryName = 'SnF_Run_'+str(attempt)+"_"+str(dims[1])+'x'+str(dims[0])+'_('+str(breed_time)+','+str(energy_gain)+','+str(breed_energy)+')_('+str(initial_sharks)+','+str(initial_fish)+')_'+str(actual_steps)
if not os.path.exists(directoryName):
    os.mkdir(directoryName)
else:
    for imgname in imgnames: #Remove all the png image files after the gif is created
        os.remove(imgname)
    sys.exit("Error: directory already exists! ")

print('Writing gif file...')
    
io.mimwrite(filename, totaldata, format= '.gif', fps = 20) #Convert all the images into a gif

for imgname in imgnames: #Remove all the png image files after the gif is created
    os.remove(imgname)

#Create and save plots of the number results
fig, axs = subplots(2)
fig.suptitle('Wa-Tor Populations')
axs[0].plot(range(actual_steps+1), fishes, label='fish')
axs[0].plot(range(actual_steps+1), sharks, label='sharks')
axs[0].legend()
axs[0].set(xlabel="", ylabel="Population")
axs[1].plot(take(fishes, range(actual_steps+1)), take(sharks, range(actual_steps+1)), marker='.')
axs[1].set(xlabel="Fish Population", ylabel="Shark Population")
#Save the plots to a file with a name that includes all the parameters of the run

plotname ='SnFplots_'+str(dims[1])+'x'+str(dims[0])+'_('+str(breed_time)+','+str(energy_gain)+','+str(breed_energy)+')_('+str(initial_sharks)+','+str(initial_fish)+')_'+str(actual_steps)+'.png'
savefig(plotname)

print('Complete!')
print('WARNING: Output files may be overwritten upon next run,')
print('to be safe be sure to move them out of the current folder!')



shutil.move(plotname,directoryName)
shutil.move(filename,directoryName)