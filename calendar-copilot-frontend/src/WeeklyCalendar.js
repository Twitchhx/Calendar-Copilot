import React from 'react';
import './WeeklyCalendar.css';

const WeeklyCalendar = ({ timeSlots }) => {
  const daysOfWeek = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];

  return (
    <div className="weekly-calendar">
      <h2>Your Proposed Weekly Calendar</h2>
      <div className="days-container">
        {daysOfWeek.map(day => (
          <div key={day} className="day">
            <h3>{day}</h3>
            <ul>
              {timeSlots[day] && timeSlots[day].length > 0 ? (
                timeSlots[day].map(slot => (
                  <li key={`${day}-${slot[0]}`}>
                    {slot[0]} - {slot[1]}
                  </li>
                ))
              ) : (
                <li>No availability</li>
              )}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WeeklyCalendar;
