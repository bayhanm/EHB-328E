from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array
import cv2, numpy as np, spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
from scipy.spatial.distance import euclidean
import os
import uuid

'''
Please read before the start!

******* Part 1 *******

This part is made for making more personalized database.
It achieves this with taking photos with 's' key input.
It takes 3 photo for each emotion with user input.
Then saves those images in FER-2013 database.
To save successfully database filepath is need to written by user first.

**********************
******* Part 2 *******

This is the emotion detection model part.
Emotion detection model is trained with FER-2013 database and CNN.
It has 7 epoch and nearly %60 accuracy

For the database part, FER-2013 database is used.
Link: https://www.kaggle.com/datasets/msambare/fer2013?resource=download

To start to this part, FER-2013 dataset must be present.

**********************
******* Part 3 *******

This part simply takes song information from spotify and saves it as csv file.
I created spotify developer account to achieve this cause.

I used Spotify's own playlists for each emotion:
Sad ID                             ------> 37i9dQZF1DX7qK8ma5wgG1?si=732c63912f384b52
Neutral (Calm) ID                  ------> 37i9dQZF1DXcy0AaElSqwE?si=74f2f25609924b65
Happy ID                           ------> 37i9dQZF1DXdPec7aLTmlC?si=4378d8923f944bd5
Horror (Fear, Suprise, Disgust) ID ------> 37i9dQZF1EIfgYPpPEriFK?si=357eb38ef4ca43e3
Angry ID                           ------> 37i9dQZF1EIgNZCaOGb0Mi?si=a114713b2e734b07

To start this part, client ID, client secret, track ID and save path must be given.

**********************
******* Part 4 *******

This part takes mean values of each column in csv file and prints it as list.
To start this part, csv file must be present and It's path must be given to the code.
Part 5 and 6 do not need this part.
Program already has mean values.

**********************
***** Part 5 & 6 *****

This is the main part of the program.
It opens camera and waits user input (space).
When the user presses space, it takes photo, predicts each emotions percentage.
For the part 6, the program uses haar cascade face detection model to detect face.
With haar cascade face detection emotions can be found much easily.
Then this percentage multiplied with the related values created in Part 3.
At the end of this multiplication, resulted list traversed at song database.
It finds euclidean distance and takes the most similar 5 song and prints to screen.

For this part I used 1.2 million song database that I found from kaggle.
Link: https://www.kaggle.com/datasets/rodolfofigueroa/spotify-12m-songs?resource=download

**********************
'''

part = input("\nWhich part to go ?"
            "[1] Adding Personal Photographs to Emotion Detection Database\n"
            "[2] Emotion Detection Model Training\n"
            "[3] Download Dataset from Spotify\n"
            "[4] Mean Calculator of Playlists Dataset\n"
            "[5] Song Suggestion WITHOUT Face Detection\n"
            "[6] Song Suggestion WITH Face Recognition\n")

if part == '1':

    # Open the camera
    cap = cv2.VideoCapture(0)

    # Set the desired width and height (256x256 is best for most users)
    desired_width = 256
    desired_height = 256

    # Enter the FER-2013 database folder path
    folder_name = 'PATH TO THE FER-2013 DATABASE'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # Define emotion labels and counters
    s_counter = 0
    folder_count = 0
    p_in_folder = 12

    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        # Get the center coordinates of the frame
        center_x, center_y = frame.shape[1] // 2, frame.shape[0] // 2

        # Calculate the cropping region
        crop_x1 = center_x - (desired_width // 2)
        crop_x2 = center_x + (desired_width // 2)
        crop_y1 = center_y - (desired_height // 2)
        crop_y2 = center_y + (desired_height // 2)

        # Crop the frame to the desired width and height
        cropped_frame = frame[crop_y1:crop_y2, crop_x1:crop_x2]

        # Resize the cropped frame to the desired width and height
        resized_frame = cv2.resize(cropped_frame, (desired_width, desired_height))

        # Convert the resized frame to grayscale
        resized_frame_gray = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

        # Display the grayscale frame
        cv2.imshow('Camera', resized_frame_gray)

        # Check for user input to take a screenshot
        key = cv2.waitKey(1)
        if key == ord('s'):
            # Generate a random filename using uuid
            random_filename = str(uuid.uuid4().hex)[:8]  # Use the first 8 characters of the UUID

            # Define the subfolder based on the counter
            folder_count = int(s_counter / p_in_folder)
            if folder_count == 0:
                subfolder_name = os.path.join(folder_name, 'angry')
            elif folder_count == 1:
                subfolder_name = os.path.join(folder_name, 'happy')
            elif folder_count == 2:
                subfolder_name = os.path.join(folder_name, 'neutral')
            elif folder_count == 3:
                subfolder_name = os.path.join(folder_name, 'sad')
            elif folder_count == 4:
                subfolder_name = os.path.join(folder_name, 'disgust')
            elif folder_count == 5:
                subfolder_name = os.path.join(folder_name, 'fear')
            elif folder_count == 6:
                subfolder_name = os.path.join(folder_name, 'surprise')

            s_counter += 1

            # Reset counter and folder if the threshold is reached
            if s_counter % p_in_folder == 0:
                folder_count = s_counter // p_in_folder
                if folder_count >= 7:
                    folder_count = 0
                    s_counter = 0

            # Create the subfolder if it doesn't exist
            if not os.path.exists(subfolder_name):
                os.makedirs(subfolder_name)

            # Save the resized grayscale frame as a 48x48 image
            resized_frame_gray_48 = cv2.resize(resized_frame_gray, (48, 48))
            filename = os.path.join(subfolder_name, f'screenshot_{random_filename}.png')
            cv2.imwrite(filename, resized_frame_gray_48)
            print(f"Screenshot saved as {filename}")

        # Break the loop if 'q' key is pressed
        if key == ord('q'):
            break

    # Release the camera and close the window
    cap.release()
    cv2.destroyAllWindows()

if part == '2':
    # Enter your train and test paths
    train_path = 'PATH TO TRAIN DATASET'
    test_path = 'PATH TO TEST DATASET'

    # Data preprocessing
    train_datagen = ImageDataGenerator(rescale=1 / 255)

    test_datagen = ImageDataGenerator(rescale=1 / 255)

    train_generator = train_datagen.flow_from_directory(
        train_path,
        target_size=(48, 48),
        batch_size=32,
        class_mode='categorical',
        color_mode='grayscale',
    )

    test_generator = test_datagen.flow_from_directory(
        test_path,
        target_size=(48, 48),
        batch_size=32,
        class_mode='categorical',
        color_mode='grayscale',
    )

    # Building the CNN model
    model = Sequential()
    model.add(Conv2D(16, (3, 3), activation='relu', input_shape=(48, 48, 1)))
    model.add(MaxPooling2D((2, 2)))
    model.add(Conv2D(32, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))
    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))

    model.add(Flatten())
    model.add(Dense(512, activation='relu'))

    model.add(Dense(7, activation='softmax'))

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Training the model
    model.fit(train_generator, epochs=7, validation_data=test_generator)

    # Saving the trained model
    model.save('emotion_model.h5')

    # Testing and printing the result of the model
    test_loss, test_accuracy = model.evaluate(test_generator)
    print(f'Test Accuracy: {test_accuracy * 100:.2f}%')

elif part == '3':

    # Needed variables
    client_id = 'ENTER YOUR CLIENT ID'
    client_secret = 'ENTER YOUR CLIENT SECRET'
    track_id = 'ENTER THE TRACK ID'
    save_path = 'ENTER THE SAVE PATH'

    # Accessing spotify database
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Getting audio features of tracks
    audio_features = sp.audio_features([track_id])[0]

    # Saving them to the csv file
    df = pd.DataFrame([audio_features])
    df.to_csv(save_path, index=False)
    print("Data saved")

elif part == '4':

    # Enter playlist csv file path for mean calculation
    other_file_path = 'ENTER YOUR PATH HERE'

    # Reading needed csv
    df_other = pd.read_csv(other_file_path)

    # Selecting only first 11 column
    df_other_selected = df_other.iloc[:, :11]

    # Calculating each columnns mean
    means = df_other_selected.mean()

    # Saving it to list
    mean_values = means.tolist()

    # Printing to mean on screen
    print("mean_values =", mean_values)

elif part == '5':

    # Opening the camera
    cap = cv2.VideoCapture(0)

    # Loading the previously made model
    emotion_model = load_model('emotion_model.h5')

    # Defining labels of the model
    emotion_labels = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}

    # Mean values created in previous step
    mean_values_angry = [0.5660000000000001, 0.81612, 4.78, -5.04438, 0.68, 0.136136, 0.068866858, 0.027984404999999993,
                         0.20739999999999995, 0.4914, 132.94598000000002]
    mean_values_happy = [0.704420, 0.732930, 5.080000, -5.391920, 0.660000, 0.085185, 0.120840, 0.003602, 0.157909,
                         0.622470, 121.296670]
    mean_values_fearful = [0.53374, 0.570164, 4.4, -9.63448, 0.42, 0.10407, 0.33629583999999996, 0.2700180076, 0.201926,
                           0.43048, 127.09622000000002]
    mean_values_sad = [0.503575, 0.373745, 4.6, -9.1181625, 0.875, 0.049756249999999995, 0.6663574999999999,
                       0.01028926275, 0.136375, 0.29327500000000006, 113.62836250000001]
    mean_values_neutral = [0.64546, 0.48525000000000007, 5.37, -9.51405, 0.55, 0.062011000000000004,
                           0.45286347000000005, 0.16932678590000005, 0.160989, 0.496, 113.98508]

    # Opening and selecting columns of 1.2m song database
    file_path = 'tracks_features.csv'
    df_selected_columns = pd.read_csv(file_path, usecols=range(9, 20))

    while True:
        # Capturing frame from webcam
        ret, frame = cap.read()

        # Displaying it while waiting input from the user
        cv2.imshow('Webcam', frame)

        key = cv2.waitKey(1)

        if key == ord(' '):

            # When the user press space, it preprocess captured image for model
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            img = cv2.resize(img, (48, 48))
            img = img_to_array(img)
            img = np.expand_dims(img, axis=0)
            img /= 255.0

            # Saves emotion percantages here
            result = emotion_model(img)

            # Refactoring fear disgust and suprise
            emotion_percentages = {
                'Angry': result[0][0],
                'Happy': result[0][3],
                'Sad': result[0][4],
                'Neutral': result[0][6],
                'Disgust + Fear + Surprise': result[0][1] + result[0][2] + result[0][5]
            }
            # Prints values to the screen for user to see
            for emotion, percentage in emotion_percentages.items():
                print(f'{emotion}: {percentage * 100:.2f}%')

            # Calculating the weighted mean using emotion_percentages
            mean_values = [
                sum(emotion_percentages[emotion].numpy() * value for emotion, value in
                    zip(emotion_percentages.keys(), emotion_values))
                for emotion_values in zip(
                    mean_values_happy,
                    mean_values_sad,
                    mean_values_angry,
                    mean_values_neutral,
                    mean_values_fearful
                )
            ]

            # Calculating Euclidean distance between mean values and each row in the 1.2m database
            df_selected_columns['distance'] = df_selected_columns.apply(lambda row: euclidean(mean_values, row.values), axis=1)

            # Finding the best 5 row
            most_similar_indices = df_selected_columns['distance'].nsmallest(5).index

            # Reads the original csv file again and takes name(1), album(2), artists(4) columns
            df_original_columns = pd.read_csv(file_path, usecols=[1, 2, 4])

            # Prints these values to the screen
            print("\n\nBest songs for current emotion: \n")
            for index in most_similar_indices:
                print("Song Name:", df_original_columns.loc[index, 'name'])
                print("Album:", df_original_columns.loc[index, 'album'])
                print("Artists:", df_original_columns.loc[index, 'artists'])
                print("---")
            break
            # Breaks after one use
elif part == '6':

    # Load the pre-trained face detection model from OpenCV
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


    # Function to detect face
    def detect_face(frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            # Calculate the center coordinates of the face
            center_x = x + w // 2
            center_y = y + h // 2

            # Calculate the top-left coordinates of the square
            square_top_left_x = max(center_x - 98, 0)
            square_top_left_y = max(center_y - 98, 0)

            # Extract the 196x196 region
            square_img = frame[square_top_left_y:square_top_left_y + 196, square_top_left_x:square_top_left_x + 196]

            # Ensure the extracted region is exactly 196x196
            if square_img.shape[0] == 196 and square_img.shape[1] == 196:
                return square_img

        return None

    # Opening the camera
    cap = cv2.VideoCapture(0)

    # Loading the previously made model
    emotion_model = load_model('emotion_model.h5')

    # Defining labels of the model
    emotion_labels = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}

    # Mean values created in previous step
    mean_values_angry = [0.5660000000000001, 0.81612, 4.78, -5.04438, 0.68, 0.136136, 0.068866858, 0.027984404999999993,
                         0.20739999999999995, 0.4914, 132.94598000000002]
    mean_values_happy = [0.704420, 0.732930, 5.080000, -5.391920, 0.660000, 0.085185, 0.120840, 0.003602, 0.157909,
                         0.622470, 121.296670]
    mean_values_fearful = [0.53374, 0.570164, 4.4, -9.63448, 0.42, 0.10407, 0.33629583999999996, 0.2700180076, 0.201926,
                           0.43048, 127.09622000000002]
    mean_values_sad = [0.503575, 0.373745, 4.6, -9.1181625, 0.875, 0.049756249999999995, 0.6663574999999999,
                       0.01028926275, 0.136375, 0.29327500000000006, 113.62836250000001]
    mean_values_neutral = [0.64546, 0.48525000000000007, 5.37, -9.51405, 0.55, 0.062011000000000004,
                           0.45286347000000005, 0.16932678590000005, 0.160989, 0.496, 113.98508]

    # Opening and selecting columns of 1.2m song database
    file_path = 'tracks_features.csv'
    df_selected_columns = pd.read_csv(file_path, usecols=range(9, 20))

    while True:
        # Capturing frame from webcam
        ret, frame = cap.read()

        # Displaying it while waiting input from the user
        cv2.imshow('Webcam', frame)

        key = cv2.waitKey(1)
        face_img = detect_face(frame)

        if cv2.waitKey(1) & 0xFF == ord(' '):
            if face_img is not None:
                cv2.imwrite('face_image.jpg', face_img)
                # When the user press space, it preprocess captured image for model
                face_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                face_img = cv2.resize(face_img, (48, 48))
                face_img = img_to_array(face_img)
                face_img = np.expand_dims(face_img, axis=0)
                face_img /= 255.0

                # Saves emotion percantages here
                result = emotion_model(face_img)

                # Refactoring fear disgust and suprise
                emotion_percentages = {
                    'Angry': result[0][0],
                    'Happy': result[0][3],
                    'Sad': result[0][4],
                    'Neutral': result[0][6],
                    'Disgust + Fear + Surprise': result[0][1] + result[0][2] + result[0][5]
                }
                # Prints values to the screen for user to see
                for emotion, percentage in emotion_percentages.items():
                    print(f'{emotion}: {percentage * 100:.2f}%')

                # Calculating the weighted mean using emotion_percentages
                mean_values = [
                    sum(emotion_percentages[emotion].numpy() * value for emotion, value in
                        zip(emotion_percentages.keys(), emotion_values))
                    for emotion_values in zip(
                        mean_values_happy,
                        mean_values_sad,
                        mean_values_angry,
                        mean_values_neutral,
                        mean_values_fearful
                    )
                ]

                # Calculating Euclidean distance between mean values and each row in the 1.2m database
                df_selected_columns['distance'] = df_selected_columns.apply(lambda row: euclidean(mean_values, row.values),
                                                                            axis=1)

                # Finding the best 5 row
                most_similar_indices = df_selected_columns['distance'].nsmallest(5).index

                # Reads the original csv file again and takes name(1), album(2), artists(4) columns
                df_original_columns = pd.read_csv(file_path, usecols=[1, 2, 4])

                # Prints these values to the screen
                print("\n\nBest songs for current emotion: \n")
                for index in most_similar_indices:
                    print("Song Name:", df_original_columns.loc[index, 'name'])
                    print("Album:", df_original_columns.loc[index, 'album'])
                    print("Artists:", df_original_columns.loc[index, 'artists'])
                    print("---")
                break
                # Breaks after one use