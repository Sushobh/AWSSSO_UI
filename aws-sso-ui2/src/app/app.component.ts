import { Component, ViewChild } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import {MatTableModule} from '@angular/material/table';
import {MatButtonModule} from '@angular/material/button';
import {ThemePalette} from '@angular/material/core';
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { NetworkResponse } from '../models/models';
import { HttpClientModule } from '@angular/common/http';
import {ProgressSpinnerMode, MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import { CommonModule } from '@angular/common';
import { delay } from 'rxjs/operators';
import { MatTable } from '@angular/material/table';
import {MatSnackBar} from '@angular/material/snack-bar';
export interface AWSProfile {
  name: string;
  roleName : string;
  expiresIn : string;
  accountId : string;
}

const URL = ''
@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule,RouterOutlet,MatSlideToggleModule,MatTableModule,MatButtonModule,HttpClientModule,MatProgressSpinnerModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
 
  @ViewChild(MatTable) myTable!: MatTable<any>;


  dataSource : AWSProfile[] = [];
  displayedColumns: string[] = ['name', 'roleName', 'expiresIn', 'accountId','refreshCredentials','login','setDefault'];
  isLoading : boolean = true;

  color: ThemePalette = 'primary';
  mode: ProgressSpinnerMode = 'indeterminate';

  constructor(private http: HttpClient,private _snackBar: MatSnackBar){
        this.getProfiles().subscribe({
          next : (res) => {
            this.dataSource = res;
             this.isLoading = false
          },
          error : (err) => {
            this.isLoading = false
          }
        })
      
  }

  clickedOnLogin(profile : AWSProfile){
    this.isLoading = true
    this.http.get<NetworkResponse>(URL+'/openLogin/'+profile.name).subscribe({
      next : () => {
         this.isLoading = false
      },
      error : (err) => {
        this.isLoading = false
      }
    })
  }

  clickedOnRefreshCreds(profile : AWSProfile){
    this.isLoading = true
    this.http.get<NetworkResponse>(URL+'/refreshCreds/'+profile.name).
    subscribe({
      next : (res) => {
        if(!res.failed){
          this.dataSource = this.mapDataToAWSProfiles(res);
        }
        if(res.status == 'CREDS_EXPIRED_SPAWN_LOGIN'){
          this._snackBar.open('Login expired, click login to refresh',undefined,{
            duration : 1000
          })
        }
        this.isLoading = false
      },
      error : (err) => {
        this.isLoading = false
      }
    })
  }

  clickedOnSetDefault(profile : AWSProfile){
    this.isLoading = true
    this.http.get<NetworkResponse>(URL+'/moveToDefault/'+profile.name).
    subscribe({
      next : (res) => {
        if(!res.failed){
          this.dataSource = this.mapDataToAWSProfiles(res);
        }
         this.isLoading = false
      },
      error : (err) => {
        this.isLoading = false
      }
    })
  }

  getProfiles(): Observable<AWSProfile[]> {
   
    return this.http.get<NetworkResponse>(URL+'/getProfiles').pipe(map(res => this.mapDataToAWSProfiles(res)),delay(1000))
   
  }

  mapDataToAWSProfiles(res : NetworkResponse) : AWSProfile[] {
    const arr = res.data as any[];
      const profiles : AWSProfile[] = [];
      arr.forEach(p => {
          profiles.push({
            name : p.name,
            accountId : p.account_id,
            roleName : p.role_name,
            expiresIn : p.expires_in
          });
      })
      return profiles;
  }
  
}
