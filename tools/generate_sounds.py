import os
import numpy as np
from scipy.io import wavfile

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_sine_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    return np.sin(2 * np.pi * frequency * t)

def generate_noise(duration, sample_rate=44100):
    return np.random.uniform(-0.3, 0.3, int(sample_rate * duration))

def apply_envelope(audio, attack=0.1, decay=0.1, sustain=0.7, release=0.1):
    samples = len(audio)
    # Ensure minimum sample counts
    attack_samples = max(1, int(attack * samples))
    decay_samples = max(1, int(decay * samples))
    sustain_samples = max(1, int(sustain * samples))
    release_samples = max(1, samples - attack_samples - decay_samples - sustain_samples)
    
    envelope = np.ones(samples)
    # Attack
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    # Decay
    envelope[attack_samples:attack_samples+decay_samples] = np.linspace(1, 0.7, decay_samples)
    # Sustain
    envelope[attack_samples+decay_samples:attack_samples+decay_samples+sustain_samples] = 0.7
    # Release
    envelope[-release_samples:] = np.linspace(0.7, 0, release_samples)
    
    return audio * envelope

def save_wav(audio, filename, sample_rate=44100):
    # Ensure audio is in -1 to 1 range
    audio = np.clip(audio, -1, 1)
    # Convert to 16-bit PCM
    audio_16bit = (audio * 32767).astype(np.int16)
    # Save file
    create_directory(os.path.dirname(filename))
    wavfile.write(filename, sample_rate, audio_16bit)

def generate_pour_sound(type="dry"):
    duration = 0.8
    noise = generate_noise(duration)
    if type == "dry":
        # High-pass filtered noise for dry ingredients
        noise = noise * np.linspace(1, 0.3, len(noise))
    else:
        # Low-pass filtered noise for liquids
        noise = noise * np.linspace(0.3, 1, len(noise))
    return apply_envelope(noise, attack=0.1, decay=0.2, sustain=0.4, release=0.3)

def generate_impact_sound():
    duration = 0.2
    freq = 150
    tone = generate_sine_wave(freq, duration)
    noise = generate_noise(duration) * 0.3
    return apply_envelope(tone + noise, attack=0.01, decay=0.05, sustain=0.1, release=0.04)

def generate_sparkle_sound():
    duration = 0.3
    audio = np.zeros(int(44100 * duration))
    for _ in range(3):
        freq = np.random.uniform(800, 2000)
        start = int(np.random.uniform(0, duration * 0.7) * 44100)
        tone = generate_sine_wave(freq, 0.1)
        end = start + len(tone)
        if end <= len(audio):
            audio[start:end] += tone * 0.3
    return apply_envelope(audio, attack=0.01, decay=0.1, sustain=0.1, release=0.1)

def generate_bubble_sound():
    duration = 0.2
    freq = np.random.uniform(100, 300)
    tone = generate_sine_wave(freq, duration)
    return apply_envelope(tone, attack=0.01, decay=0.05, sustain=0.1, release=0.04)

def generate_steam_sound():
    duration = 0.5
    noise = generate_noise(duration)
    # High-pass filter simulation
    noise = noise * np.linspace(0.5, 1, len(noise))
    return apply_envelope(noise, attack=0.1, decay=0.1, sustain=0.2, release=0.1)

def generate_ambient_sound():
    duration = 5.0
    noise = generate_noise(duration) * 0.3
    low_freq = generate_sine_wave(60, duration) * 0.2
    return apply_envelope(noise + low_freq, attack=0.5, decay=0.5, sustain=3.5, release=0.5)

def main():
    base_path = "assets/sounds"
    
    # Generate mixing sounds
    for type in ["flour", "sugar", "cocoa"]:
        save_wav(generate_pour_sound("dry"), f"{base_path}/mixing/pour_{type}.wav")
    for type in ["milk", "vanilla", "eggs"]:
        save_wav(generate_pour_sound("liquid"), f"{base_path}/mixing/pour_{type}.wav")
    
    # Generate impact sounds
    for i in range(2):
        save_wav(generate_impact_sound(), f"{base_path}/mixing/flour_impact_{i}.wav")
        save_wav(generate_impact_sound(), f"{base_path}/mixing/liquid_splash_{i}.wav")
    
    # Generate sparkle sounds
    for i in range(3):
        save_wav(generate_sparkle_sound(), f"{base_path}/effects/sparkle{i+1}.wav")
    
    # Generate baking sounds
    for i in range(3):
        save_wav(generate_bubble_sound(), f"{base_path}/baking/bubble{i+1}.wav")
    for i in range(2):
        save_wav(generate_steam_sound(), f"{base_path}/baking/steam{i+1}.wav")
    
    # Generate ambient sounds
    save_wav(generate_ambient_sound(), f"{base_path}/ambient/kitchen_loop.wav")
    save_wav(generate_ambient_sound(), f"{base_path}/ambient/oven_hum.wav")

if __name__ == "__main__":
    main()
    print("Generated placeholder sound files successfully!") 