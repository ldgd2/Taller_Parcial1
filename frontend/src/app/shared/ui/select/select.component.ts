import { Component, Input, forwardRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ControlValueAccessor, NG_VALUE_ACCESSOR, FormsModule } from '@angular/forms';

export interface SelectOption {
  label: string;
  value: any;
}

@Component({
  selector: 'app-select',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="input-group">
      <label *ngIf="label" [for]="id" class="input-label" [class.has-error]="error">
        {{ label }} <span *ngIf="required" class="text-danger">*</span>
      </label>
      
      <div class="select-wrapper">
        <select 
          [id]="id"
          [disabled]="disabled"
          [value]="value"
          (change)="onChangeCb($event)"
          (blur)="onTouched()"
          class="form-select"
          [class.is-invalid]="error">
          <option value="" disabled selected *ngIf="placeholder">{{ placeholder }}</option>
          <option *ngFor="let opt of options" [value]="opt.value">{{ opt.label }}</option>
        </select>
        <!-- Custom down arrow indicator -->
        <span class="select-arrow">
          <svg viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd"></path>
          </svg>
        </span>
      </div>
      <span class="error-msg" *ngIf="error">{{ error }}</span>
    </div>
  `,
  styleUrls: ['./select.component.scss'],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => SelectComponent),
      multi: true
    }
  ]
})
export class SelectComponent implements ControlValueAccessor {
  @Input() id: string = `select-${Math.random().toString(36).substr(2, 9)}`;
  @Input() label: string = '';
  @Input() placeholder: string = 'Seleccione una opción';
  @Input() options: SelectOption[] = [];
  @Input() error: string | null = null;
  @Input() required: boolean = false;

  value: any = '';
  disabled: boolean = false;

  onChange: any = () => {};
  onTouched: any = () => {};

  onChangeCb(event: Event) {
    const val = (event.target as HTMLSelectElement).value;
    this.value = val;
    this.onChange(val);
  }

  // ControlValueAccessor methods
  writeValue(value: any): void {
    this.value = value || '';
  }
  registerOnChange(fn: any): void {
    this.onChange = fn;
  }
  registerOnTouched(fn: any): void {
    this.onTouched = fn;
  }
  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }
}
