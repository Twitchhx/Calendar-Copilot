import React, { useState } from 'react';
import axios from 'axios';
import './App.css';
import WeeklyCalendar from './WeeklyCalendar';

function App() {
  const [availability, setAvailability] = useState('');
  const [timeSlots, setTimeSlots] = useState({});
  const [error, setError] = useState('');
  const [submitted, setSubmitted] = useState(false); // Track if availability has been submitted
  const [saved, setSaved] = useState(false); // Track if availability has been saved

  const handleInputChange = (event) => {
    setAvailability(event.target.value);
  };

  const extractTimeSlots = () => {
    // Clear previous time slots and error messages
    setTimeSlots({});
    setError('');
    setSubmitted('');
    setSaved('');

    // Perform input validation
    if (!availability.trim()) {
      setError('Please enter your availability.');
      return;
    }

    // Send availability data to the backend server to extract time slots
    axios.post('http://localhost:5000/extract-time-slots', { availability })
      .then(response => {
        if (response.data.error) {
          setError(response.data.error);
        } else {
          // Update time slots state with the extracted time slots
          setTimeSlots(response.data.time_slots);
          setSubmitted(true); // Mark availability as submitted
        }
      })
      .catch(error => {
        setError('An error occurred while processing your request. Please try again.');
        console.error('Error:', error);
      });
  };

  const saveToDatabase = () => {
    if (Object.keys(timeSlots).length === 0) {
      setError('No time slots to save.');
      return;
    }

    // Send time slots to the backend server to save availability
    axios.post('http://localhost:5000/save-availability', { availability, time_slots: timeSlots })
      .then(response => {
        if (response.data.error) {
          setError(response.data.error);
        } else {
          setSaved(true); // Mark availability as saved
        }
      })
      .catch(error => {
        setError('An error occurred while saving your availability. Please try again.');
        console.error('Error:', error);
      });
  };

  return (
    <div className="App">
      <h1>Calendar Co-pilot</h1>
      {!submitted && (
        <div>
          <p>Enter your availability (Comma Separated):</p>
          <textarea
            className='txt'
            value={availability}
            onChange={handleInputChange}
            rows="4"
            cols="50"
            placeholder="e.g., I am available between noon and 4pm on weekends, after 7 pm to midnight on Monday and Wednesday, and after 9pm otherwise."
          />
          <button className='btn' onClick={extractTimeSlots}>Submit</button>
          {error && <p className="error">{error}</p>}
        </div>
      )}
      
      {submitted && Object.keys(timeSlots).length > 0 && (
        <div>
          <WeeklyCalendar timeSlots={timeSlots} />
          {!saved && <button className='btn' onClick={saveToDatabase}>Save Availability</button>}
          {saved && <p className="success">Availability saved successfully!</p>}
        </div>
      )}
    </div>
  );
}

export default App;
