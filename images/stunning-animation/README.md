# Eye-Opening Animation for Stunning Landing Page

## Overview

This animation creates an interactive "awareness" effect where the model's eye opens in response to user interaction (email signup submission). The effect creates the impression that the model is becoming aware of and acknowledging the visitor's action.

## Deliverables

### Video Files
- **`eye-opening-animation.mp4`** - The main animation (1 second duration)
  - Starts with eyes closed
  - Smooth transition through intermediate frames
  - Ends with eyes fully open
  - Optimized for web with H.264 codec

- **`eye-opening-demo.mp4`** - Demo version with adjusted timing
  - Longer pause at the beginning (0.5s closed)
  - Quick eye-opening sequence (0.6s)
  - Holds on open eyes (2s)
  - Good for previewing the effect

### Individual Frames (in `frames-for-web/`)
All frames are 2752x1536 PNG images:
- `00-closed.png` - Eyes fully closed (starting state)
- `01-barely-open.png` - Just beginning to open
- `02-quarter-open.png` - 25% open
- `03-half-open.png` - 50% open
- `04-three-quarter-open.png` - 75% open
- `05-fully-open.png` - Eyes fully open (ending state)

## Implementation Options

### Option 1: Video Element (Simplest)
Use the MP4 file directly with a video element:

```jsx
const [hasSubmitted, setHasSubmitted] = useState(false);
const videoRef = useRef(null);

const handleSubmit = (email) => {
  // Your email submission logic
  setHasSubmitted(true);
  videoRef.current?.play();
};

return (
  <div className="hero-container">
    {!hasSubmitted ? (
      <img src="/images/00-closed.png" alt="Stunning" />
    ) : (
      <video
        ref={videoRef}
        src="/videos/eye-opening-animation.mp4"
        muted
        playsInline
        onEnded={() => {/* Keep showing final frame */}}
      />
    )}
  </div>
);
```

### Option 2: Frame Sequence Animation (More Control)
Use the individual frames for frame-by-frame animation:

```jsx
const frames = [
  '/images/00-closed.png',
  '/images/01-barely-open.png',
  '/images/02-quarter-open.png',
  '/images/03-half-open.png',
  '/images/04-three-quarter-open.png',
  '/images/05-fully-open.png'
];

const [currentFrame, setCurrentFrame] = useState(0);

const animateEyeOpening = () => {
  let frame = 0;
  const interval = setInterval(() => {
    frame++;
    setCurrentFrame(frame);
    if (frame >= frames.length - 1) {
      clearInterval(interval);
    }
  }, 100); // 100ms per frame = 0.6s total animation
};

const handleSubmit = (email) => {
  // Your email submission logic
  animateEyeOpening();
};

return (
  <div className="hero-container">
    <img src={frames[currentFrame]} alt="Stunning" />
  </div>
);
```

### Option 3: Canvas Animation (Best Performance)
Preload all frames and use canvas for smooth rendering:

```jsx
// Preload frames
useEffect(() => {
  frames.forEach(src => {
    const img = new Image();
    img.src = src;
  });
}, []);

// Use canvas or CSS sprite sheet for optimal performance
```

## Technical Specifications

- **Resolution**: 2752x1536 (landscape)
- **Aspect Ratio**: 16:9 (approximately)
- **Format**: PNG (frames), MP4/H.264 (video)
- **Animation Duration**: ~0.6-1.0 seconds
- **Frame Count**: 6 frames total

## Recommended Timing

For the best psychological effect:
1. **Initial state**: Eyes closed (static)
2. **Trigger**: User clicks submit button
3. **Animation**: 0.6-1.0 second eye-opening sequence
4. **Final state**: Eyes open (hold indefinitely or until next interaction)

## Performance Optimization

- Preload all images/video before showing the signup form
- Use `loading="eager"` for the first frame
- Consider using WebP format for frames (reduce file size by ~30%)
- Implement lazy loading for frames that aren't immediately visible

## Next Steps

1. Choose your implementation approach
2. Optimize images for web (consider WebP conversion)
3. Add the animation trigger to your email signup handler
4. Test across different devices and browsers
5. Consider adding subtle sound effects for enhanced impact

---

**Note**: The animation is designed to be subtle yet impactful. The key is the timing—it should feel responsive and natural, not jarring or artificial.
